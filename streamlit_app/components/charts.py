"""
Componentes de gráficos para DriveAnalytics
============================================
Gráficos reutilizables con Plotly.
"""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from typing import Optional

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))
from config import CHART_COLORS, ESTADO_CONFIG, CHART_CONFIG


def _apply_chart_theme(fig: go.Figure) -> go.Figure:
    """Aplica tema oscuro consistente a los gráficos."""
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#fafafa"),
        legend=dict(
            bgcolor="rgba(0,0,0,0)",
            font=dict(color="#fafafa")
        ),
        margin=dict(l=20, r=20, t=40, b=20),
    )
    return fig


def chart_distribucion_estados(df: pd.DataFrame) -> Optional[go.Figure]:
    """
    Gráfico de dona mostrando distribución de estados.
    
    Args:
        df: DataFrame con los datos.
    
    Returns:
        Figura de Plotly o None si no hay datos.
    """
    if "estado" not in df.columns or df.empty:
        return None
    
    estado_counts = df["estado"].value_counts().reset_index()
    estado_counts.columns = ["Estado", "Cantidad"]
    
    # Obtener colores de configuración
    colors = [ESTADO_CONFIG.get(e, {}).get("color", "#888888") 
              for e in estado_counts["Estado"]]
    
    fig = px.pie(
        estado_counts,
        values="Cantidad",
        names="Estado",
        hole=0.4,
        color_discrete_sequence=colors,
        title="Distribución por Estado"
    )
    
    fig.update_traces(
        textposition="inside",
        textinfo="percent+value",
        hovertemplate="<b>%{label}</b><br>Cantidad: %{value}<br>Porcentaje: %{percent}<extra></extra>"
    )
    
    return _apply_chart_theme(fig)


def chart_vehiculos_por_marca(df: pd.DataFrame) -> Optional[go.Figure]:
    """
    Gráfico de barras horizontal mostrando vehículos por marca.
    
    Args:
        df: DataFrame con los datos.
    
    Returns:
        Figura de Plotly o None si no hay datos.
    """
    if "marca" not in df.columns or df.empty:
        return None
    
    marca_counts = df["marca"].value_counts().reset_index()
    marca_counts.columns = ["Marca", "Cantidad"]
    marca_counts = marca_counts.sort_values("Cantidad", ascending=True)
    
    fig = px.bar(
        marca_counts,
        x="Cantidad",
        y="Marca",
        orientation="h",
        color="Cantidad",
        color_continuous_scale="Blues",
        title="Vehículos por Marca"
    )
    
    fig.update_layout(showlegend=False, coloraxis_showscale=False)
    fig.update_traces(
        hovertemplate="<b>%{y}</b><br>Cantidad: %{x}<extra></extra>"
    )
    
    return _apply_chart_theme(fig)


def chart_precio_por_año(df: pd.DataFrame) -> Optional[go.Figure]:
    """
    Gráfico de línea mostrando precio promedio por año.
    
    Args:
        df: DataFrame con los datos.
    
    Returns:
        Figura de Plotly o None si no hay datos.
    """
    if "año" not in df.columns or "precio_cop" not in df.columns or df.empty:
        return None
    
    precio_por_año = df.groupby("año")["precio_cop"].mean().reset_index()
    precio_por_año.columns = ["Año", "Precio Promedio"]
    precio_por_año = precio_por_año.sort_values("Año")
    
    fig = px.line(
        precio_por_año,
        x="Año",
        y="Precio Promedio",
        markers=True,
        title="Precio Promedio por Año",
        color_discrete_sequence=[CHART_COLORS[0]]
    )
    
    fig.update_traces(
        line=dict(width=3),
        marker=dict(size=10),
        hovertemplate="<b>Año %{x}</b><br>Precio: $%{y:,.0f}<extra></extra>"
    )
    
    fig.update_yaxes(tickformat="$,.0f")
    
    return _apply_chart_theme(fig)


def chart_km_vs_precio(df: pd.DataFrame) -> Optional[go.Figure]:
    """
    Gráfico de dispersión: kilometraje vs precio.
    
    Args:
        df: DataFrame con los datos.
    
    Returns:
        Figura de Plotly o None si no hay datos.
    """
    if "kilometraje" not in df.columns or "precio_cop" not in df.columns or df.empty:
        return None
    
    fig = px.scatter(
        df,
        x="kilometraje",
        y="precio_cop",
        color="marca" if "marca" in df.columns else None,
        size="cv" if "cv" in df.columns else None,
        hover_data=["modelo", "año"] if all(c in df.columns for c in ["modelo", "año"]) else None,
        title="Relación Kilometraje vs Precio",
        color_discrete_sequence=CHART_COLORS
    )
    
    fig.update_traces(
        hovertemplate="<b>%{customdata[0]}</b> (%{customdata[1]})<br>Km: %{x:,.0f}<br>Precio: $%{y:,.0f}<extra></extra>"
    )
    
    fig.update_xaxes(title="Kilometraje")
    fig.update_yaxes(title="Precio (COP)", tickformat="$,.0f")
    
    return _apply_chart_theme(fig)


def chart_distribucion_transmision(df: pd.DataFrame) -> Optional[go.Figure]:
    """
    Gráfico de barras mostrando distribución por transmisión.
    
    Args:
        df: DataFrame con los datos.
    
    Returns:
        Figura de Plotly o None si no hay datos.
    """
    if "transmisión" not in df.columns or df.empty:
        return None
    
    trans_counts = df["transmisión"].value_counts().reset_index()
    trans_counts.columns = ["Transmisión", "Cantidad"]
    
    fig = px.bar(
        trans_counts,
        x="Transmisión",
        y="Cantidad",
        color="Transmisión",
        title="Distribución por Transmisión",
        color_discrete_sequence=CHART_COLORS
    )
    
    fig.update_layout(showlegend=False)
    fig.update_traces(
        hovertemplate="<b>%{x}</b><br>Cantidad: %{y}<extra></extra>"
    )
    
    return _apply_chart_theme(fig)


def chart_precio_por_marca(df: pd.DataFrame) -> Optional[go.Figure]:
    """
    Box plot mostrando distribución de precios por marca.
    
    Args:
        df: DataFrame con los datos.
    
    Returns:
        Figura de Plotly o None si no hay datos.
    """
    if "marca" not in df.columns or "precio_cop" not in df.columns or df.empty:
        return None
    
    fig = px.box(
        df,
        x="marca",
        y="precio_cop",
        color="marca",
        title="Distribución de Precios por Marca",
        color_discrete_sequence=CHART_COLORS
    )
    
    fig.update_layout(showlegend=False)
    fig.update_xaxes(title="Marca")
    fig.update_yaxes(title="Precio (COP)", tickformat="$,.0f")
    
    return _apply_chart_theme(fig)


def render_chart(fig: Optional[go.Figure], height: int = 400) -> None:
    """
    Renderiza un gráfico en Streamlit.
    
    Args:
        fig: Figura de Plotly.
        height: Altura del gráfico.
    """
    if fig is None:
        st.warning("No hay datos suficientes para mostrar este gráfico.")
        return
    
    st.plotly_chart(
        fig, 
        use_container_width=CHART_CONFIG["use_container_width"],
        height=height
    )
