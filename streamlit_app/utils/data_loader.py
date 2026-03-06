"""
Módulo para carga y filtrado de datos
======================================
Centraliza toda la lógica de acceso a datos.
"""

import pandas as pd
import streamlit as st
from pathlib import Path
from typing import Optional, Dict, Any, List

import sys
sys.path.append(str(Path(__file__).parent.parent))
from config import DATA_FILE


@st.cache_data(ttl=300)  # Cache por 5 minutos
def load_data(file_path: Optional[Path] = None) -> pd.DataFrame:
    """
    Carga el dataset desde CSV con caché.
    
    Args:
        file_path: Ruta al archivo CSV. Si es None, usa DATA_FILE de config.
    
    Returns:
        DataFrame con los datos del inventario.
    """
    path = file_path or DATA_FILE
    
    try:
        df = pd.read_csv(path)
        
        # Asegurar tipos de datos correctos
        if "año" in df.columns:
            df["año"] = pd.to_numeric(df["año"], errors="coerce").astype("Int64")
        if "kilometraje" in df.columns:
            df["kilometraje"] = pd.to_numeric(df["kilometraje"], errors="coerce").astype("Int64")
        if "cv" in df.columns:
            df["cv"] = pd.to_numeric(df["cv"], errors="coerce").astype("Int64")
        if "precio_cop" in df.columns:
            df["precio_cop"] = pd.to_numeric(df["precio_cop"], errors="coerce").astype("Int64")
        if "motor" in df.columns:
            df["motor"] = pd.to_numeric(df["motor"], errors="coerce")
        if "peso_kg" in df.columns:
            df["peso_kg"] = pd.to_numeric(df["peso_kg"], errors="coerce")
            
        return df
    
    except FileNotFoundError:
        st.error(f"❌ No se encontró el archivo: {path}")
        return pd.DataFrame()
    except Exception as e:
        st.error(f"❌ Error al cargar datos: {e}")
        return pd.DataFrame()


def get_filtered_data(
    df: pd.DataFrame, 
    filters: Dict[str, Any]
) -> pd.DataFrame:
    """
    Aplica filtros al DataFrame.
    
    Args:
        df: DataFrame original.
        filters: Diccionario con {columna: valor(es)} para filtrar.
    
    Returns:
        DataFrame filtrado.
    """
    df_filtered = df.copy()
    
    for column, value in filters.items():
        if value is None or (isinstance(value, list) and len(value) == 0):
            continue
            
        if column not in df_filtered.columns:
            continue
        
        # Filtro por lista de valores
        if isinstance(value, list):
            df_filtered = df_filtered[df_filtered[column].isin(value)]
        
        # Filtro por rango (tupla de min, max)
        elif isinstance(value, tuple) and len(value) == 2:
            min_val, max_val = value
            if min_val is not None:
                df_filtered = df_filtered[df_filtered[column] >= min_val]
            if max_val is not None:
                df_filtered = df_filtered[df_filtered[column] <= max_val]
        
        # Filtro por valor único
        else:
            df_filtered = df_filtered[df_filtered[column] == value]
    
    return df_filtered


def get_unique_values(df: pd.DataFrame, column: str) -> List:
    """
    Obtiene valores únicos de una columna.
    
    Args:
        df: DataFrame.
        column: Nombre de la columna.
    
    Returns:
        Lista de valores únicos ordenados.
    """
    if column not in df.columns:
        return []
    
    values = df[column].dropna().unique().tolist()
    
    # Intentar ordenar (si son comparables)
    try:
        return sorted(values)
    except TypeError:
        return values


def get_column_range(df: pd.DataFrame, column: str) -> tuple:
    """
    Obtiene el rango (min, max) de una columna numérica.
    
    Args:
        df: DataFrame.
        column: Nombre de la columna.
    
    Returns:
        Tupla (min, max).
    """
    if column not in df.columns:
        return (0, 0)
    
    col = df[column].dropna()
    return (col.min(), col.max())
