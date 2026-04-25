"""
Simulacion, validacion y optimizacion para DriveAnalytics.
"""

from __future__ import annotations

from itertools import product
from typing import Any, Dict, List

import numpy as np
import pandas as pd


def _safe_mean(df: pd.DataFrame, column: str, default: float = 0.0) -> float:
    if column not in df.columns:
        return default
    value = pd.to_numeric(df[column], errors="coerce").dropna().mean()
    return float(value) if pd.notna(value) else default


def _estimate_sell_through(df: pd.DataFrame) -> float:
    if df.empty or "estado" not in df.columns:
        return 0.0
    sold = (df["estado"].astype(str).str.lower() == "vendido").sum()
    return float(sold / len(df)) if len(df) else 0.0


def get_historical_baseline(
    df: pd.DataFrame,
    reference_df: pd.DataFrame | None = None,
) -> Dict[str, float]:
    """Genera una linea base historica simple usando inventario y referencia historica."""
    avg_price = _safe_mean(df, "precio_cop", default=0.0)
    historical_source = reference_df if reference_df is not None and not reference_df.empty else df
    sell_through = _estimate_sell_through(historical_source)
    if sell_through <= 0:
        sell_through = _estimate_sell_through(df)
    if sell_through <= 0:
        # Fallback conservador cuando no hay vendidos en el dataset.
        sell_through = 0.12
    total_units = float(len(df))
    return {
        "avg_price": avg_price,
        "sell_through": sell_through,
        "total_units": total_units,
        # Ratio costo/precio aproximado para estimar margen.
        "cost_ratio": 0.82,
        # Elasticidad precio-demanda: descuento del 1% sube demanda esperada ~1.1%.
        "discount_elasticity": 1.1,
    }


def simulate_deterministic(
    df: pd.DataFrame,
    discount_pct: float,
    reconditioning_cost_mcop: float,
    market_change_pct: float,
    regulation_cost_pct: float,
    crisis_impact_pct: float,
    reference_df: pd.DataFrame | None = None,
) -> Dict[str, float]:
    """Simula un escenario deterministico de ingresos, utilidad y riesgo de inventario."""
    baseline = get_historical_baseline(df, reference_df=reference_df)

    base_price = baseline["avg_price"]
    total_units = baseline["total_units"]
    base_sell_through = baseline["sell_through"]
    cost_ratio = baseline["cost_ratio"]
    discount_elasticity = baseline["discount_elasticity"]

    demand_factor = (
        (1.0 + (discount_elasticity * discount_pct / 100.0))
        * (1.0 + market_change_pct / 100.0)
        * (1.0 - crisis_impact_pct / 100.0)
    )
    expected_sell_through = float(np.clip(base_sell_through * demand_factor, 0.0, 1.0))
    units_sold = total_units * expected_sell_through

    adjusted_price = base_price * (1.0 - discount_pct / 100.0) * (1.0 + market_change_pct / 100.0)
    revenue = units_sold * adjusted_price

    acquisition_cost = units_sold * adjusted_price * cost_ratio
    reconditioning_cost = units_sold * reconditioning_cost_mcop * 1_000_000
    regulation_cost = revenue * (regulation_cost_pct / 100.0)

    expected_profit = revenue - acquisition_cost - reconditioning_cost - regulation_cost
    unsold_units = max(total_units - units_sold, 0.0)

    return {
        "units_sold": round(units_sold, 2),
        "sell_through": round(expected_sell_through, 4),
        "avg_sale_price": round(adjusted_price, 2),
        "revenue": round(revenue, 2),
        "expected_profit": round(expected_profit, 2),
        "unsold_units": round(unsold_units, 2),
    }


def simulate_stochastic(
    df: pd.DataFrame,
    discount_pct: float,
    reconditioning_cost_mcop: float,
    market_change_pct: float,
    regulation_cost_pct: float,
    crisis_impact_pct: float,
    reference_df: pd.DataFrame | None = None,
    n_simulations: int = 1000,
    market_volatility_pct: float = 4.0,
    demand_volatility_pct: float = 6.0,
) -> Dict[str, float]:
    """Ejecuta Monte Carlo alrededor del escenario base para capturar incertidumbre."""
    profits: List[float] = []
    sold_units: List[float] = []

    for _ in range(n_simulations):
        market_shock = np.random.normal(loc=market_change_pct, scale=market_volatility_pct)
        crisis_shock = max(
            0.0,
            np.random.normal(loc=crisis_impact_pct, scale=max(demand_volatility_pct / 2.0, 1.0)),
        )
        discount_shock = max(0.0, np.random.normal(loc=discount_pct, scale=1.0))

        result = simulate_deterministic(
            df=df,
            discount_pct=discount_shock,
            reconditioning_cost_mcop=reconditioning_cost_mcop,
            market_change_pct=market_shock,
            regulation_cost_pct=regulation_cost_pct,
            crisis_impact_pct=crisis_shock,
            reference_df=reference_df,
        )
        profits.append(result["expected_profit"])
        sold_units.append(result["units_sold"])

    profits_arr = np.array(profits)
    sold_units_arr = np.array(sold_units)

    return {
        "profit_mean": float(np.mean(profits_arr)),
        "profit_std": float(np.std(profits_arr)),
        "profit_p10": float(np.percentile(profits_arr, 10)),
        "profit_p50": float(np.percentile(profits_arr, 50)),
        "profit_p90": float(np.percentile(profits_arr, 90)),
        "units_sold_mean": float(np.mean(sold_units_arr)),
        "units_sold_std": float(np.std(sold_units_arr)),
        "simulations": int(n_simulations),
    }


def validate_model(df: pd.DataFrame, reference_df: pd.DataFrame | None = None) -> Dict[str, float]:
    """Valida el modelo base contra metricas historicas observadas del dataset."""
    baseline_pred = simulate_deterministic(
        df=df,
        discount_pct=0.0,
        reconditioning_cost_mcop=0.8,
        market_change_pct=0.0,
        regulation_cost_pct=0.0,
        crisis_impact_pct=0.0,
        reference_df=reference_df,
    )

    actual_units_sold = 0.0
    if "estado" in df.columns:
        actual_units_sold = float((df["estado"].astype(str).str.lower() == "vendido").sum())

    actual_avg_price = _safe_mean(df, "precio_cop", default=0.0)

    pred_units_sold = baseline_pred["units_sold"]
    pred_avg_price = baseline_pred["avg_sale_price"]

    units_mae = abs(actual_units_sold - pred_units_sold)
    price_mae = abs(actual_avg_price - pred_avg_price)
    units_mape = (units_mae / actual_units_sold * 100.0) if actual_units_sold > 0 else 0.0
    price_mape = (price_mae / actual_avg_price * 100.0) if actual_avg_price > 0 else 0.0

    return {
        "actual_units_sold": actual_units_sold,
        "pred_units_sold": pred_units_sold,
        "units_mae": units_mae,
        "units_mape": units_mape,
        "actual_avg_price": actual_avg_price,
        "pred_avg_price": pred_avg_price,
        "price_mae": price_mae,
        "price_mape": price_mape,
    }


def optimize_decision(
    df: pd.DataFrame,
    market_change_pct: float,
    regulation_cost_pct: float,
    crisis_impact_pct: float,
    reference_df: pd.DataFrame | None = None,
    risk_aversion: float = 0.25,
    discount_options: List[float] | None = None,
    reconditioning_options: List[float] | None = None,
    n_simulations: int = 300,
) -> Dict[str, Any]:
    """Busca la mejor politica de descuento/reacondicionamiento maximizando utilidad ajustada por riesgo."""
    discount_grid = discount_options or [0, 2, 4, 6, 8, 10, 12]
    reconditioning_grid = reconditioning_options or [0.2, 0.5, 0.8, 1.2, 1.8, 2.5]

    rows: List[Dict[str, float]] = []
    for discount, reconditioning in product(discount_grid, reconditioning_grid):
        stoch = simulate_stochastic(
            df=df,
            discount_pct=float(discount),
            reconditioning_cost_mcop=float(reconditioning),
            market_change_pct=market_change_pct,
            regulation_cost_pct=regulation_cost_pct,
            crisis_impact_pct=crisis_impact_pct,
            reference_df=reference_df,
            n_simulations=n_simulations,
        )
        utility_score = (
            stoch["profit_mean"]
            - (risk_aversion * stoch["profit_std"])
            - (150_000 * max(len(df) - stoch["units_sold_mean"], 0.0))
        )
        rows.append(
            {
                "discount_pct": float(discount),
                "reconditioning_mcop": float(reconditioning),
                "profit_mean": stoch["profit_mean"],
                "profit_std": stoch["profit_std"],
                "units_sold_mean": stoch["units_sold_mean"],
                "utility_score": utility_score,
            }
        )

    results_df = pd.DataFrame(rows).sort_values(by="utility_score", ascending=False).reset_index(drop=True)
    best = results_df.iloc[0].to_dict() if not results_df.empty else {}

    return {
        "best_decision": best,
        "ranking": results_df,
    }


def generate_decision_recommendations(
    df: pd.DataFrame,
    market_change_pct: float,
    regulation_cost_pct: float,
    crisis_impact_pct: float,
    reference_df: pd.DataFrame | None = None,
    n_simulations: int = 400,
) -> pd.DataFrame:
    """Compara estrategias candidatas y devuelve la opcion recomendada."""
    strategies = [
        {"estrategia": "Conservadora", "discount_pct": 2.0, "reconditioning_mcop": 0.5, "risk_weight": 0.40},
        {"estrategia": "Balanceada", "discount_pct": 6.0, "reconditioning_mcop": 1.0, "risk_weight": 0.30},
        {"estrategia": "Agresiva", "discount_pct": 10.0, "reconditioning_mcop": 1.8, "risk_weight": 0.20},
    ]

    rows = []
    for s in strategies:
        stoch = simulate_stochastic(
            df=df,
            discount_pct=s["discount_pct"],
            reconditioning_cost_mcop=s["reconditioning_mcop"],
            market_change_pct=market_change_pct,
            regulation_cost_pct=regulation_cost_pct,
            crisis_impact_pct=crisis_impact_pct,
            reference_df=reference_df,
            n_simulations=n_simulations,
        )
        decision_score = stoch["profit_mean"] - (s["risk_weight"] * stoch["profit_std"])
        rows.append(
            {
                "estrategia": s["estrategia"],
                "descuento_pct": s["discount_pct"],
                "reacond_mcop": s["reconditioning_mcop"],
                "utilidad_esperada": stoch["profit_mean"],
                "riesgo_std": stoch["profit_std"],
                "p10_utilidad": stoch["profit_p10"],
                "p90_utilidad": stoch["profit_p90"],
                "puntaje_decision": decision_score,
            }
        )

    result = pd.DataFrame(rows).sort_values(by="puntaje_decision", ascending=False).reset_index(drop=True)
    return result