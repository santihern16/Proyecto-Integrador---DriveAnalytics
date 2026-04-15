"""
Componente de filtros para el sidebar y filtros inline
=======================================================
Filtros reutilizables para la aplicación.
"""

import streamlit as st
import pandas as pd
from typing import Dict, Any, List, Optional

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))
from config import FILTERABLE_COLUMNS, COLUMN_LABELS
from utils.data_loader import get_unique_values, get_column_range


def _clear_sidebar_filter_state(df: pd.DataFrame) -> None:
    """Restablece el estado de los widgets de filtros del sidebar."""
    if "marca" in df.columns:
        st.session_state["filter_marca"] = []

    if "estado" in df.columns:
        st.session_state["filter_estado"] = []

    if "transmisión" in df.columns:
        st.session_state["filter_transmision"] = []

    if "año" in df.columns:
        min_año, max_año = get_column_range(df, "año")
        if pd.notna(min_año) and pd.notna(max_año):
            st.session_state["filter_año"] = (int(min_año), int(max_año))

    if "precio_cop" in df.columns:
        min_precio, max_precio = get_column_range(df, "precio_cop")
        if pd.notna(min_precio) and pd.notna(max_precio):
            st.session_state["filter_precio"] = (
                int(min_precio / 1_000_000),
                int(max_precio / 1_000_000),
            )

    if "kilometraje" in df.columns:
        min_km, max_km = get_column_range(df, "kilometraje")
        if pd.notna(min_km) and pd.notna(max_km):
            st.session_state["filter_km"] = (
                int(min_km / 1_000),
                int(max_km / 1_000),
            )


def render_sidebar_filters(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Renderiza filtros en el sidebar.
    
    Args:
        df: DataFrame con los datos.
    
    Returns:
        Diccionario con los filtros seleccionados.
    """
    st.sidebar.header("🔍 Filtros")
    
    filters = {}
    
    # Filtro por marca
    if "marca" in df.columns:
        marcas = get_unique_values(df, "marca")
        selected_marcas = st.sidebar.multiselect(
            "Marca",
            options=marcas,
            default=[],
            key="filter_marca"
        )
        if selected_marcas:
            filters["marca"] = selected_marcas
    
    # Filtro por estado
    if "estado" in df.columns:
        estados = get_unique_values(df, "estado")
        selected_estados = st.sidebar.multiselect(
            "Estado",
            options=estados,
            default=[],
            key="filter_estado"
        )
        if selected_estados:
            filters["estado"] = selected_estados
    
    # Filtro por transmisión
    if "transmisión" in df.columns:
        transmisiones = get_unique_values(df, "transmisión")
        selected_trans = st.sidebar.multiselect(
            "Transmisión",
            options=transmisiones,
            default=[],
            key="filter_transmision"
        )
        if selected_trans:
            filters["transmisión"] = selected_trans
    
    # Filtro por año (rango)
    if "año" in df.columns:
        min_año, max_año = get_column_range(df, "año")
        if pd.notna(min_año) and pd.notna(max_año):
            año_range = st.sidebar.slider(
                "Año",
                min_value=int(min_año),
                max_value=int(max_año),
                value=(int(min_año), int(max_año)),
                key="filter_año"
            )
            if año_range != (int(min_año), int(max_año)):
                filters["año"] = año_range
    
    # Filtro por precio (rango)
    if "precio_cop" in df.columns:
        min_precio, max_precio = get_column_range(df, "precio_cop")
        if pd.notna(min_precio) and pd.notna(max_precio):
            precio_range = st.sidebar.slider(
                "Precio (Millones COP)",
                min_value=int(min_precio / 1_000_000),
                max_value=int(max_precio / 1_000_000),
                value=(int(min_precio / 1_000_000), int(max_precio / 1_000_000)),
                key="filter_precio"
            )
            # Convertir de millones a valor real
            precio_min = precio_range[0] * 1_000_000
            precio_max = precio_range[1] * 1_000_000
            if (precio_min, precio_max) != (min_precio, max_precio):
                filters["precio_cop"] = (precio_min, precio_max)
    
    # Filtro por kilometraje (rango)
    if "kilometraje" in df.columns:
        min_km, max_km = get_column_range(df, "kilometraje")
        if pd.notna(min_km) and pd.notna(max_km):
            km_range = st.sidebar.slider(
                "Kilometraje (miles)",
                min_value=int(min_km / 1_000),
                max_value=int(max_km / 1_000),
                value=(int(min_km / 1_000), int(max_km / 1_000)),
                key="filter_km"
            )
            km_min = km_range[0] * 1_000
            km_max = km_range[1] * 1_000
            if (km_min, km_max) != (min_km, max_km):
                filters["kilometraje"] = (km_min, km_max)
    
    # Botón para limpiar filtros
    st.sidebar.divider()
    st.sidebar.button(
        "🔄 Limpiar Filtros",
        use_container_width=True,
        on_click=_clear_sidebar_filter_state,
        args=(df,),
    )
    
    return filters


def render_inline_filters(
    df: pd.DataFrame,
    columns: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Renderiza filtros en línea (horizontal).
    
    Args:
        df: DataFrame con los datos.
        columns: Lista de columnas a filtrar. Si es None, usa FILTERABLE_COLUMNS.
    
    Returns:
        Diccionario con los filtros seleccionados.
    """
    columns_to_filter = columns or FILTERABLE_COLUMNS
    filters = {}
    
    cols = st.columns(len(columns_to_filter))
    
    for i, col_name in enumerate(columns_to_filter):
        if col_name not in df.columns:
            continue
            
        with cols[i]:
            values = get_unique_values(df, col_name)
            label = COLUMN_LABELS.get(col_name, col_name.title())
            
            selected = st.selectbox(
                label,
                options=["Todos"] + values,
                key=f"inline_filter_{col_name}"
            )
            
            if selected != "Todos":
                filters[col_name] = selected
    
    return filters
