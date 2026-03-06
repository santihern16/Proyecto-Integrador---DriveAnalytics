"""
Componentes de tablas y tarjetas de datos
==========================================
Visualización de datos tabulares y detalles de vehículos.
"""

import streamlit as st
import pandas as pd
from typing import Optional, List

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))
from config import COLUMN_LABELS, ESTADO_CONFIG, format_currency, format_km


def render_data_table(
    df: pd.DataFrame,
    columns: Optional[List[str]] = None,
    height: int = 400,
    show_index: bool = False
) -> None:
    """
    Renderiza una tabla de datos interactiva.
    
    Args:
        df: DataFrame con los datos.
        columns: Lista de columnas a mostrar. Si es None, muestra todas.
        height: Altura de la tabla.
        show_index: Mostrar índice.
    """
    if df.empty:
        st.info("No hay datos para mostrar.")
        return
    
    # Seleccionar columnas
    if columns:
        display_df = df[columns].copy()
    else:
        display_df = df.copy()
    
    # Renombrar columnas con etiquetas amigables
    display_df = display_df.rename(columns=COLUMN_LABELS)
    
    # Configuración de columnas para st.dataframe
    column_config = {}
    
    if "Precio (COP)" in display_df.columns:
        column_config["Precio (COP)"] = st.column_config.NumberColumn(
            "Precio (COP)",
            format="$%d",
            help="Precio en pesos colombianos"
        )
    
    if "Kilometraje" in display_df.columns:
        column_config["Kilometraje"] = st.column_config.NumberColumn(
            "Kilometraje",
            format="%d km",
            help="Kilometraje del vehículo"
        )
    
    if "Motor (L)" in display_df.columns:
        column_config["Motor (L)"] = st.column_config.NumberColumn(
            "Motor (L)",
            format="%.1f L",
            help="Cilindrada del motor en litros"
        )
    
    if "Estado" in display_df.columns:
        column_config["Estado"] = st.column_config.TextColumn(
            "Estado",
            help="Estado actual del vehículo"
        )
    
    st.dataframe(
        display_df,
        use_container_width=True,
        height=height,
        hide_index=not show_index,
        column_config=column_config
    )


def render_vehicle_card(vehicle: pd.Series) -> None:
    """
    Renderiza una tarjeta con detalles de un vehículo.
    
    Args:
        vehicle: Serie de pandas con los datos del vehículo.
    """
    estado = vehicle.get("estado", "desconocido")
    estado_config = ESTADO_CONFIG.get(estado, {"color": "#888", "icon": "❓", "label": "Desconocido"})
    
    marca = vehicle.get("marca", "N/A")
    modelo = vehicle.get("modelo", "N/A")
    año = vehicle.get("año", "N/A")
    placa = vehicle.get("placa", "N/A")
    precio = vehicle.get("precio_cop", 0)
    km = vehicle.get("kilometraje", 0)
    motor = vehicle.get("motor", 0)
    cv = vehicle.get("cv", 0)
    transmision = vehicle.get("transmisión", "N/A")
    peso = vehicle.get("peso_kg", 0)
    
    st.markdown(
        f"""
        <div style="
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            border-radius: 15px;
            padding: 20px;
            border: 1px solid #333;
            margin-bottom: 15px;
        ">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px;">
                <div>
                    <h3 style="margin: 0; color: #fff;">{marca} {modelo}</h3>
                    <span style="color: #888;">Año {año} · {placa}</span>
                </div>
                <div style="
                    background-color: {estado_config['color']}33;
                    border: 1px solid {estado_config['color']};
                    padding: 5px 15px;
                    border-radius: 20px;
                    color: {estado_config['color']};
                    font-weight: bold;
                ">
                    {estado_config['icon']} {estado_config['label']}
                </div>
            </div>
            
            <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 15px; margin-top: 15px;">
                <div style="text-align: center;">
                    <div style="font-size: 1.5em; font-weight: bold; color: #4CAF50;">
                        {format_currency(precio)}
                    </div>
                    <div style="color: #888; font-size: 0.9em;">Precio</div>
                </div>
                <div style="text-align: center;">
                    <div style="font-size: 1.5em; font-weight: bold; color: #2196F3;">
                        {format_km(km)}
                    </div>
                    <div style="color: #888; font-size: 0.9em;">Kilometraje</div>
                </div>
                <div style="text-align: center;">
                    <div style="font-size: 1.5em; font-weight: bold; color: #FF9800;">
                        {cv} CV
                    </div>
                    <div style="color: #888; font-size: 0.9em;">Potencia</div>
                </div>
            </div>
            
            <div style="margin-top: 15px; padding-top: 15px; border-top: 1px solid #333;">
                <span style="color: #888;">Motor: </span><span style="color: #fff;">{motor}L</span>
                <span style="margin: 0 10px; color: #333;">|</span>
                <span style="color: #888;">Transmisión: </span><span style="color: #fff;">{transmision}</span>
                <span style="margin: 0 10px; color: #333;">|</span>
                <span style="color: #888;">Peso: </span><span style="color: #fff;">{peso} kg</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


def render_vehicle_list(df: pd.DataFrame, max_items: int = 5) -> None:
    """
    Renderiza una lista de vehículos como tarjetas.
    
    Args:
        df: DataFrame con los datos.
        max_items: Número máximo de items a mostrar.
    """
    if df.empty:
        st.info("No hay vehículos para mostrar.")
        return
    
    for idx, row in df.head(max_items).iterrows():
        render_vehicle_card(row)
    
    if len(df) > max_items:
        st.info(f"Mostrando {max_items} de {len(df)} vehículos. Ajusta los filtros para ver más.")
