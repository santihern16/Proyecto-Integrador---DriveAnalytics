"""
Componentes de tarjetas KPI
============================
Tarjetas métricas reutilizables.
"""

import streamlit as st
from typing import Dict, Any, Optional

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))
from config import format_currency, format_km, ESTADO_CONFIG


def render_single_kpi(
    label: str,
    value: Any,
    delta: Optional[Any] = None,
    delta_color: str = "normal",
    icon: str = "",
    help_text: Optional[str] = None
) -> None:
    """
    Renderiza una tarjeta KPI individual.
    
    Args:
        label: Etiqueta del KPI.
        value: Valor del KPI.
        delta: Cambio/delta opcional.
        delta_color: Color del delta ("normal", "inverse", "off").
        icon: Emoji/icono opcional.
        help_text: Texto de ayuda opcional.
    """
    display_label = f"{icon} {label}" if icon else label
    st.metric(
        label=display_label,
        value=value,
        delta=delta,
        delta_color=delta_color,
        help=help_text
    )


def render_kpi_cards(kpis: Dict[str, Any]) -> None:
    """
    Renderiza todas las tarjetas KPI principales.
    
    Args:
        kpis: Diccionario con los KPIs calculados.
    """
    # Primera fila: métricas de inventario
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        render_single_kpi(
            label="Total Vehículos",
            value=kpis.get("total_vehiculos", 0),
            icon="🚗",
            help_text="Número total de vehículos en el inventario"
        )
    
    with col2:
        disponibles = kpis.get("disponibles", 0)
        render_single_kpi(
            label="Disponibles",
            value=disponibles,
            icon=ESTADO_CONFIG["disponible"]["icon"],
            help_text="Vehículos disponibles para venta"
        )
    
    with col3:
        vendidos = kpis.get("vendidos", 0)
        render_single_kpi(
            label="Vendidos",
            value=vendidos,
            icon=ESTADO_CONFIG["vendido"]["icon"],
            help_text="Vehículos vendidos"
        )
    
    with col4:
        en_taller = kpis.get("en_taller", 0)
        render_single_kpi(
            label="En Taller",
            value=en_taller,
            icon=ESTADO_CONFIG["taller"]["icon"],
            help_text="Vehículos en mantenimiento"
        )
    
    # Segunda fila: métricas financieras
    st.divider()
    col5, col6, col7, col8 = st.columns(4)
    
    with col5:
        valor_inv = kpis.get("valor_inventario", 0)
        render_single_kpi(
            label="Valor Inventario",
            value=format_currency(valor_inv),
            icon="💰",
            help_text="Valor total del inventario"
        )
    
    with col6:
        precio_prom = kpis.get("precio_promedio", 0)
        render_single_kpi(
            label="Precio Promedio",
            value=format_currency(precio_prom),
            icon="📊",
            help_text="Precio promedio por vehículo"
        )
    
    with col7:
        km_prom = kpis.get("km_promedio", 0)
        render_single_kpi(
            label="Km Promedio",
            value=format_km(km_prom),
            icon="🛣️",
            help_text="Kilometraje promedio de los vehículos"
        )
    
    with col8:
        marcas = kpis.get("marcas_unicas", 0)
        render_single_kpi(
            label="Marcas",
            value=marcas,
            icon="🏭",
            help_text="Número de marcas diferentes"
        )


def render_estado_badges(kpis: Dict[str, Any]) -> None:
    """
    Renderiza badges de estado en formato horizontal.
    
    Args:
        kpis: Diccionario con los KPIs.
    """
    cols = st.columns(3)
    
    estados = [
        ("disponible", "disponibles"),
        ("vendido", "vendidos"),
        ("taller", "en_taller"),
    ]
    
    for i, (estado_key, kpi_key) in enumerate(estados):
        config = ESTADO_CONFIG[estado_key]
        count = kpis.get(kpi_key, 0)
        
        with cols[i]:
            st.markdown(
                f"""
                <div style="
                    background-color: {config['color']}22;
                    border-left: 4px solid {config['color']};
                    padding: 10px 15px;
                    border-radius: 0 8px 8px 0;
                ">
                    <span style="font-size: 1.5em;">{config['icon']}</span>
                    <span style="font-size: 1.2em; font-weight: bold; margin-left: 10px;">
                        {count}
                    </span>
                    <span style="color: #888; margin-left: 5px;">
                        {config['label']}
                    </span>
                </div>
                """,
                unsafe_allow_html=True
            )
