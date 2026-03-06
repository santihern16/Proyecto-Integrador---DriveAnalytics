"""
DriveAnalytics - Dashboard de Inventario
=========================================
Aplicación principal de Streamlit.

Ejecutar con:
    streamlit run streamlit_app/app.py
"""

import streamlit as st
import sys
from pathlib import Path

# Agregar el directorio de la app al path
APP_DIR = Path(__file__).parent
sys.path.insert(0, str(APP_DIR))

from config import APP_CONFIG
from utils import load_data, get_filtered_data, calculate_kpis
from components import (
    render_sidebar_filters,
    render_kpi_cards,
    render_data_table,
    render_vehicle_card,
)
from components.charts import (
    chart_distribucion_estados,
    chart_vehiculos_por_marca,
    chart_precio_por_año,
    chart_km_vs_precio,
    chart_distribucion_transmision,
    chart_precio_por_marca,
    render_chart,
)
from components.data_table import render_vehicle_list

# ─────────────────────────────────────────────
# CONFIGURACIÓN DE PÁGINA
# ─────────────────────────────────────────────
st.set_page_config(
    page_title=APP_CONFIG["title"],
    page_icon=APP_CONFIG["page_icon"],
    layout=APP_CONFIG["layout"],
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────
# ESTILOS PERSONALIZADOS
# ─────────────────────────────────────────────
st.markdown("""
<style>
    /* Ocultar menú de hamburguesa y footer */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Estilo para el header */
    .main-header {
        font-size: 2.5em;
        font-weight: bold;
        color: #ffffff;
        margin-bottom: 0;
    }
    
    .sub-header {
        font-size: 1.2em;
        color: #888888;
        margin-top: 0;
    }
    
    /* Cards de métricas */
    [data-testid="metric-container"] {
        background-color: #262730;
        border-radius: 10px;
        padding: 15px;
        border: 1px solid #333;
    }
    
    /* Tabs personalizados */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    
    .stTabs [data-baseweb="tab"] {
        background-color: #262730;
        border-radius: 8px;
        padding: 10px 20px;
    }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# CARGAR DATOS
# ─────────────────────────────────────────────
@st.cache_data
def get_data():
    return load_data()

df = get_data()

if df.empty:
    st.error("❌ No se pudieron cargar los datos. Verifica que existe el archivo `inventario_limpio.csv`.")
    st.stop()


# ─────────────────────────────────────────────
# SIDEBAR - FILTROS
# ─────────────────────────────────────────────
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/car.png", width=60)
    st.title("DriveAnalytics")
    st.caption("Dashboard de Inventario")
    st.divider()

filters = render_sidebar_filters(df)
df_filtered = get_filtered_data(df, filters)

# Mostrar contador de filtros activos
with st.sidebar:
    if filters:
        st.info(f"🔍 {len(filters)} filtro(s) activo(s)")
        st.caption(f"Mostrando {len(df_filtered)} de {len(df)} vehículos")


# ─────────────────────────────────────────────
# HEADER PRINCIPAL
# ─────────────────────────────────────────────
st.markdown(f'<h1 class="main-header">{APP_CONFIG["title"]}</h1>', unsafe_allow_html=True)
st.markdown(f'<p class="sub-header">{APP_CONFIG["subtitle"]}</p>', unsafe_allow_html=True)
st.divider()


# ─────────────────────────────────────────────
# KPIs PRINCIPALES
# ─────────────────────────────────────────────
kpis = calculate_kpis(df_filtered)
render_kpi_cards(kpis)
st.divider()


# ─────────────────────────────────────────────
# TABS DE CONTENIDO
# ─────────────────────────────────────────────
tab_dashboard, tab_analisis, tab_inventario, tab_detalle = st.tabs([
    "📊 Dashboard",
    "📈 Análisis",
    "📋 Inventario",
    "🔍 Detalle"
])


# ── TAB: Dashboard ───────────────────────────
with tab_dashboard:
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Distribución por Estado")
        render_chart(chart_distribucion_estados(df_filtered))
    
    with col2:
        st.subheader("Vehículos por Marca")
        render_chart(chart_vehiculos_por_marca(df_filtered))
    
    col3, col4 = st.columns(2)
    
    with col3:
        st.subheader("Precio Promedio por Año")
        render_chart(chart_precio_por_año(df_filtered))
    
    with col4:
        st.subheader("Distribución por Transmisión")
        render_chart(chart_distribucion_transmision(df_filtered))


# ── TAB: Análisis ────────────────────────────
with tab_analisis:
    st.subheader("Análisis de Precios")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Kilometraje vs Precio")
        render_chart(chart_km_vs_precio(df_filtered), height=450)
    
    with col2:
        st.markdown("#### Distribución de Precios por Marca")
        render_chart(chart_precio_por_marca(df_filtered), height=450)
    
    st.divider()
    
    # Estadísticas adicionales
    st.subheader("📊 Estadísticas Detalladas")
    
    col_stats1, col_stats2, col_stats3 = st.columns(3)
    
    with col_stats1:
        st.markdown("**Por Marca**")
        if "marca" in df_filtered.columns:
            stats_marca = df_filtered.groupby("marca").agg({
                "modelo": "count",
                "precio_cop": "mean"
            }).round(0)
            stats_marca.columns = ["Cantidad", "Precio Prom."]
            stats_marca["Precio Prom."] = stats_marca["Precio Prom."].apply(lambda x: f"${x:,.0f}")
            st.dataframe(stats_marca, use_container_width=True)
    
    with col_stats2:
        st.markdown("**Por Estado**")
        if "estado" in df_filtered.columns:
            stats_estado = df_filtered.groupby("estado").agg({
                "modelo": "count",
                "precio_cop": "sum"
            }).round(0)
            stats_estado.columns = ["Cantidad", "Valor Total"]
            stats_estado["Valor Total"] = stats_estado["Valor Total"].apply(lambda x: f"${x:,.0f}")
            st.dataframe(stats_estado, use_container_width=True)
    
    with col_stats3:
        st.markdown("**Por Transmisión**")
        if "transmisión" in df_filtered.columns:
            stats_trans = df_filtered.groupby("transmisión").agg({
                "modelo": "count",
                "precio_cop": "mean"
            }).round(0)
            stats_trans.columns = ["Cantidad", "Precio Prom."]
            stats_trans["Precio Prom."] = stats_trans["Precio Prom."].apply(lambda x: f"${x:,.0f}")
            st.dataframe(stats_trans, use_container_width=True)


# ── TAB: Inventario ──────────────────────────
with tab_inventario:
    st.subheader("📋 Inventario Completo")
    
    # Opciones de vista
    col_opts1, col_opts2 = st.columns([3, 1])
    
    with col_opts2:
        view_mode = st.selectbox(
            "Vista",
            options=["Tabla", "Tarjetas"],
            key="view_mode"
        )
    
    if view_mode == "Tabla":
        # Selección de columnas a mostrar
        all_columns = df_filtered.columns.tolist()
        default_columns = ["marca", "modelo", "año", "estado", "kilometraje", "precio_cop", "placa"]
        default_columns = [c for c in default_columns if c in all_columns]
        
        selected_columns = st.multiselect(
            "Columnas a mostrar",
            options=all_columns,
            default=default_columns,
            key="table_columns"
        )
        
        if selected_columns:
            render_data_table(df_filtered, columns=selected_columns, height=500)
        else:
            render_data_table(df_filtered, height=500)
        
        # Botón de descarga
        csv = df_filtered.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Descargar CSV",
            data=csv,
            file_name="inventario_filtrado.csv",
            mime="text/csv",
        )
    
    else:  # Vista de tarjetas
        st.markdown(f"*Mostrando {min(10, len(df_filtered))} de {len(df_filtered)} vehículos*")
        render_vehicle_list(df_filtered, max_items=10)


# ── TAB: Detalle ─────────────────────────────
with tab_detalle:
    st.subheader("🔍 Buscar Vehículo")
    
    col_search1, col_search2 = st.columns(2)
    
    with col_search1:
        # Búsqueda por placa
        placas = df_filtered["placa"].dropna().unique().tolist()
        selected_placa = st.selectbox(
            "Buscar por Placa",
            options=["Seleccionar..."] + sorted(placas),
            key="search_placa"
        )
    
    with col_search2:
        # Búsqueda por modelo
        modelos = df_filtered["modelo"].dropna().unique().tolist()
        selected_modelo = st.selectbox(
            "Buscar por Modelo",
            options=["Seleccionar..."] + sorted(modelos),
            key="search_modelo"
        )
    
    # Mostrar vehículo seleccionado
    if selected_placa != "Seleccionar...":
        vehicle = df_filtered[df_filtered["placa"] == selected_placa]
        if not vehicle.empty:
            st.divider()
            st.markdown("### Detalle del Vehículo")
            render_vehicle_card(vehicle.iloc[0])
    
    elif selected_modelo != "Seleccionar...":
        vehicles = df_filtered[df_filtered["modelo"] == selected_modelo]
        if not vehicles.empty:
            st.divider()
            st.markdown(f"### Vehículos modelo {selected_modelo}")
            for _, vehicle in vehicles.iterrows():
                render_vehicle_card(vehicle)


# ─────────────────────────────────────────────
# FOOTER
# ─────────────────────────────────────────────
st.divider()
st.markdown(
    """
    <div style="text-align: center; color: #666; padding: 20px;">
        <p>DriveAnalytics © 2024 | Dashboard de Inventario de Concesionario</p>
        <p style="font-size: 0.8em;">Desarrollado con Streamlit + Plotly</p>
    </div>
    """,
    unsafe_allow_html=True
)
