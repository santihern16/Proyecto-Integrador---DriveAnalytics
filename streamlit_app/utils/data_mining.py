"""
Mineria de datos para DriveAnalytics.
"""

from __future__ import annotations

from collections import Counter
from itertools import combinations
from typing import Any, Dict, List, Tuple

import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, r2_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.tree import DecisionTreeRegressor


def clean_and_prepare_data(df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """Limpia, transforma y reduce outliers para mejorar la calidad analitica."""
    if df.empty:
        return df.copy(), {
            "rows_before": 0,
            "rows_after": 0,
            "rows_removed_outliers": 0,
            "missing_before": 0,
            "missing_after": 0,
        }

    cleaned = df.copy()
    rows_before = len(cleaned)
    missing_before = int(cleaned.isna().sum().sum())

    numeric_cols = cleaned.select_dtypes(include=[np.number]).columns.tolist()
    categorical_cols = cleaned.select_dtypes(exclude=[np.number]).columns.tolist()

    for col in numeric_cols:
        median = cleaned[col].median()
        if pd.notna(median):
            cleaned[col] = cleaned[col].fillna(median)

    for col in categorical_cols:
        mode = cleaned[col].mode(dropna=True)
        if not mode.empty:
            cleaned[col] = cleaned[col].fillna(mode.iloc[0])

    outlier_columns = [
        c for c in ["precio_cop", "kilometraje", "cv", "motor", "peso_kg"] if c in cleaned.columns
    ]
    if not outlier_columns:
        outlier_columns = numeric_cols[:4]

    mask = pd.Series(True, index=cleaned.index)
    for col in outlier_columns:
        series = pd.to_numeric(cleaned[col], errors="coerce")
        q1 = series.quantile(0.25)
        q3 = series.quantile(0.75)
        iqr = q3 - q1
        if pd.isna(iqr) or iqr == 0:
            continue
        lower = q1 - 1.5 * iqr
        upper = q3 + 1.5 * iqr
        mask &= series.between(lower, upper, inclusive="both")

    cleaned = cleaned[mask].copy()
    rows_after = len(cleaned)
    missing_after = int(cleaned.isna().sum().sum())

    if "precio_cop" in cleaned.columns and "kilometraje" in cleaned.columns:
        km_base = pd.to_numeric(cleaned["kilometraje"], errors="coerce").replace(0, np.nan)
        price_base = pd.to_numeric(cleaned["precio_cop"], errors="coerce")
        cleaned["precio_por_km"] = (price_base / km_base).replace([np.inf, -np.inf], np.nan).fillna(0)

    report = {
        "rows_before": rows_before,
        "rows_after": rows_after,
        "rows_removed_outliers": rows_before - rows_after,
        "missing_before": missing_before,
        "missing_after": missing_after,
    }
    return cleaned, report


def identify_behavior_patterns(df: pd.DataFrame) -> Dict[str, pd.DataFrame]:
    """Detecta patrones de comportamiento y relaciones utiles para decision."""
    results: Dict[str, pd.DataFrame] = {}
    if df.empty:
        return results

    combo_cols = [c for c in ["marca", "estado", "transmisión"] if c in df.columns]
    if combo_cols:
        patterns = (
            df.groupby(combo_cols)
            .size()
            .reset_index(name="conteo")
            .sort_values(by="conteo", ascending=False)
            .head(15)
        )
        results["patrones_frecuentes"] = patterns

    if "estado" in df.columns and "marca" in df.columns:
        sold_mask = df["estado"].astype(str).str.lower() == "vendido"
        sold_rate = (
            df.assign(vendido=sold_mask.astype(int))
            .groupby("marca")
            .agg(
                total_vehiculos=("vendido", "size"),
                tasa_venta=("vendido", "mean"),
                precio_promedio=("precio_cop", "mean") if "precio_cop" in df.columns else ("vendido", "size"),
            )
            .sort_values(by="tasa_venta", ascending=False)
            .reset_index()
        )
        results["tasa_venta_por_marca"] = sold_rate

    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    if len(numeric_cols) >= 2:
        corr = df[numeric_cols].corr(numeric_only=True)
        corr_pairs = []
        for i, col_a in enumerate(corr.columns):
            for col_b in corr.columns[i + 1 :]:
                corr_pairs.append(
                    {
                        "variable_a": col_a,
                        "variable_b": col_b,
                        "correlacion": corr.loc[col_a, col_b],
                        "correlacion_abs": abs(corr.loc[col_a, col_b]),
                    }
                )
        corr_df = pd.DataFrame(corr_pairs).sort_values(by="correlacion_abs", ascending=False).head(12)
        results["correlaciones_relevantes"] = corr_df

    return results


def _model_features(df: pd.DataFrame, target: str) -> Tuple[List[str], List[str], pd.DataFrame, pd.Series]:
    feature_cols = [c for c in ["año", "kilometraje", "cv", "motor", "peso_kg", "marca", "transmisión", "estado"] if c in df.columns and c != target]
    if not feature_cols or target not in df.columns:
        return [], [], pd.DataFrame(), pd.Series(dtype=float)

    X = df[feature_cols].copy()
    y = pd.to_numeric(df[target], errors="coerce")
    valid_mask = y.notna()
    X = X[valid_mask]
    y = y[valid_mask]

    numeric_features = [c for c in feature_cols if pd.api.types.is_numeric_dtype(X[c])]
    categorical_features = [c for c in feature_cols if c not in numeric_features]
    return numeric_features, categorical_features, X, y


def train_predictive_models(df: pd.DataFrame) -> Dict[str, Any]:
    """Entrena modelos de regresion y arbol de decision para predecir precio."""
    if df.empty or "precio_cop" not in df.columns:
        return {"status": "error", "message": "No hay datos suficientes o falta la columna precio_cop."}

    numeric_features, categorical_features, X, y = _model_features(df, target="precio_cop")
    if X.empty or len(X) < 40:
        return {"status": "error", "message": "Se requieren al menos 40 filas válidas para entrenar modelos."}

    preprocessor = ColumnTransformer(
        transformers=[
            (
                "num",
                Pipeline(
                    steps=[
                        ("imputer", SimpleImputer(strategy="median")),
                        ("scaler", StandardScaler()),
                    ]
                ),
                numeric_features,
            ),
            (
                "cat",
                Pipeline(
                    steps=[
                        ("imputer", SimpleImputer(strategy="most_frequent")),
                        ("onehot", OneHotEncoder(handle_unknown="ignore")),
                    ]
                ),
                categorical_features,
            ),
        ]
    )

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    reg_pipeline = Pipeline(
        steps=[
            ("preprocessor", preprocessor),
            ("model", LinearRegression()),
        ]
    )
    tree_pipeline = Pipeline(
        steps=[
            ("preprocessor", preprocessor),
            ("model", DecisionTreeRegressor(max_depth=6, min_samples_leaf=6, random_state=42)),
        ]
    )

    reg_pipeline.fit(X_train, y_train)
    tree_pipeline.fit(X_train, y_train)

    pred_reg = reg_pipeline.predict(X_test)
    pred_tree = tree_pipeline.predict(X_test)

    metrics_df = pd.DataFrame(
        [
            {
                "modelo": "Regresión Lineal",
                "r2": float(r2_score(y_test, pred_reg)),
                "mae": float(mean_absolute_error(y_test, pred_reg)),
            },
            {
                "modelo": "Árbol de Decisión",
                "r2": float(r2_score(y_test, pred_tree)),
                "mae": float(mean_absolute_error(y_test, pred_tree)),
            },
        ]
    )

    sample_predictions = pd.DataFrame(
        {
            "precio_real": y_test.values,
            "pred_regresion": np.round(pred_reg, 0),
            "pred_arbol": np.round(pred_tree, 0),
        }
    ).head(12)

    return {
        "status": "ok",
        "metrics": metrics_df,
        "sample_predictions": sample_predictions,
        "rows_train": int(len(X_train)),
        "rows_test": int(len(X_test)),
    }


def segment_entities(df: pd.DataFrame, n_clusters: int = 4) -> Dict[str, Any]:
    """Segmenta entidades por clustering usando variables numéricas de negocio."""
    if df.empty:
        return {"status": "error", "message": "No hay datos para segmentar."}

    cluster_features = [c for c in ["precio_cop", "kilometraje", "año", "cv", "motor", "peso_kg"] if c in df.columns]
    if len(cluster_features) < 2:
        return {"status": "error", "message": "Se requieren al menos 2 variables numéricas para clustering."}

    model_df = df[cluster_features].copy()
    model_df = model_df.apply(pd.to_numeric, errors="coerce")
    model_df = model_df.fillna(model_df.median(numeric_only=True))

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(model_df)

    kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    labels = kmeans.fit_predict(X_scaled)

    segmented = df.copy()
    segmented["segmento"] = labels

    profile = (
        segmented.groupby("segmento")
        .agg(
            vehiculos=("segmento", "size"),
            precio_promedio=("precio_cop", "mean") if "precio_cop" in segmented.columns else ("segmento", "size"),
            km_promedio=("kilometraje", "mean") if "kilometraje" in segmented.columns else ("segmento", "size"),
            anio_promedio=("año", "mean") if "año" in segmented.columns else ("segmento", "size"),
        )
        .reset_index()
        .sort_values(by="vehiculos", ascending=False)
    )

    return {
        "status": "ok",
        "segmented_df": segmented,
        "profile": profile,
        "inertia": float(kmeans.inertia_),
        "features": cluster_features,
    }


def generate_association_rules(
    df: pd.DataFrame,
    min_support: float = 0.05,
    min_confidence: float = 0.35,
    top_n: int = 20,
) -> pd.DataFrame:
    """Genera reglas de asociacion A -> B con soporte, confianza y lift."""
    if df.empty:
        return pd.DataFrame()

    base_cols = [c for c in ["marca", "modelo", "estado", "transmisión"] if c in df.columns]
    if len(base_cols) < 2:
        return pd.DataFrame()

    transactions: List[List[str]] = []
    for _, row in df[base_cols].iterrows():
        items = [f"{col}={row[col]}" for col in base_cols if pd.notna(row[col])]
        if len(items) >= 2:
            transactions.append(items)

    n_transactions = len(transactions)
    if n_transactions == 0:
        return pd.DataFrame()

    item_counter = Counter()
    pair_counter = Counter()

    for trans in transactions:
        unique_items = list(dict.fromkeys(trans))
        item_counter.update(unique_items)
        pair_counter.update(combinations(sorted(unique_items), 2))

    rules_rows: List[Dict[str, Any]] = []
    for (a, b), pair_count in pair_counter.items():
        support_ab = pair_count / n_transactions
        if support_ab < min_support:
            continue

        support_a = item_counter[a] / n_transactions
        support_b = item_counter[b] / n_transactions
        conf_a_b = pair_count / item_counter[a] if item_counter[a] else 0.0
        conf_b_a = pair_count / item_counter[b] if item_counter[b] else 0.0
        lift_a_b = (conf_a_b / support_b) if support_b > 0 else 0.0
        lift_b_a = (conf_b_a / support_a) if support_a > 0 else 0.0

        if conf_a_b >= min_confidence:
            rules_rows.append(
                {
                    "antecedente": a,
                    "consecuente": b,
                    "soporte": support_ab,
                    "confianza": conf_a_b,
                    "lift": lift_a_b,
                    "casos": pair_count,
                }
            )
        if conf_b_a >= min_confidence:
            rules_rows.append(
                {
                    "antecedente": b,
                    "consecuente": a,
                    "soporte": support_ab,
                    "confianza": conf_b_a,
                    "lift": lift_b_a,
                    "casos": pair_count,
                }
            )

    if not rules_rows:
        return pd.DataFrame()

    rules_df = pd.DataFrame(rules_rows)
    rules_df = rules_df.sort_values(by=["lift", "confianza", "soporte"], ascending=False).head(top_n)
    return rules_df.reset_index(drop=True)