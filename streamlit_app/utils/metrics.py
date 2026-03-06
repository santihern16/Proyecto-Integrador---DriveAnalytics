"""
Módulo para cálculo de métricas y KPIs
=======================================
Funciones para calcular estadísticas del inventario.
"""

import pandas as pd
from typing import Dict, Any


def calculate_kpis(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Calcula los KPIs principales del inventario.
    
    Args:
        df: DataFrame con los datos.
    
    Returns:
        Diccionario con KPIs calculados.
    """
    if df.empty:
        return {
            "total_vehiculos": 0,
            "disponibles": 0,
            "vendidos": 0,
            "en_taller": 0,
            "valor_inventario": 0,
            "precio_promedio": 0,
            "km_promedio": 0,
            "marcas_unicas": 0,
        }
    
    return {
        "total_vehiculos": len(df),
        "disponibles": len(df[df["estado"] == "disponible"]) if "estado" in df.columns else 0,
        "vendidos": len(df[df["estado"] == "vendido"]) if "estado" in df.columns else 0,
        "en_taller": len(df[df["estado"] == "taller"]) if "estado" in df.columns else 0,
        "valor_inventario": df["precio_cop"].sum() if "precio_cop" in df.columns else 0,
        "precio_promedio": df["precio_cop"].mean() if "precio_cop" in df.columns else 0,
        "km_promedio": df["kilometraje"].mean() if "kilometraje" in df.columns else 0,
        "marcas_unicas": df["marca"].nunique() if "marca" in df.columns else 0,
    }


def get_summary_stats(df: pd.DataFrame) -> Dict[str, pd.DataFrame]:
    """
    Genera estadísticas resumidas por diferentes agrupaciones.
    
    Args:
        df: DataFrame con los datos.
    
    Returns:
        Diccionario con DataFrames de resumen.
    """
    summaries = {}
    
    # Por marca
    if "marca" in df.columns:
        summaries["por_marca"] = df.groupby("marca").agg({
            "modelo": "count",
            "precio_cop": ["mean", "sum"] if "precio_cop" in df.columns else "count",
            "kilometraje": "mean" if "kilometraje" in df.columns else "count",
        }).round(0)
        summaries["por_marca"].columns = ["Cantidad", "Precio Promedio", "Valor Total", "Km Promedio"]
    
    # Por estado
    if "estado" in df.columns:
        summaries["por_estado"] = df.groupby("estado").agg({
            "modelo": "count",
            "precio_cop": "sum" if "precio_cop" in df.columns else "count",
        })
        summaries["por_estado"].columns = ["Cantidad", "Valor Total"]
    
    # Por año
    if "año" in df.columns:
        summaries["por_año"] = df.groupby("año").agg({
            "modelo": "count",
            "precio_cop": "mean" if "precio_cop" in df.columns else "count",
        }).round(0)
        summaries["por_año"].columns = ["Cantidad", "Precio Promedio"]
    
    # Por transmisión
    if "transmisión" in df.columns:
        summaries["por_transmision"] = df.groupby("transmisión").agg({
            "modelo": "count",
            "precio_cop": "mean" if "precio_cop" in df.columns else "count",
        }).round(0)
        summaries["por_transmision"].columns = ["Cantidad", "Precio Promedio"]
    
    return summaries


def get_top_vehicles(
    df: pd.DataFrame, 
    by: str = "precio_cop", 
    n: int = 5, 
    ascending: bool = False
) -> pd.DataFrame:
    """
    Obtiene los top N vehículos ordenados por una columna.
    
    Args:
        df: DataFrame con los datos.
        by: Columna para ordenar.
        n: Número de resultados.
        ascending: Orden ascendente o descendente.
    
    Returns:
        DataFrame con los top N vehículos.
    """
    if by not in df.columns:
        return df.head(n)
    
    return df.nlargest(n, by) if not ascending else df.nsmallest(n, by)
