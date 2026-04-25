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

from config import APP_CONFIG, format_currency
from utils import (
    load_data,
    get_filtered_data,
    calculate_kpis,
    simulate_deterministic,
    simulate_stochastic,
    validate_model,
    optimize_decision,
    generate_decision_recommendations,
    clean_and_prepare_data,
    identify_behavior_patterns,
    train_predictive_models,
    segment_entities,
    generate_association_rules,
)
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
tab_dashboard, tab_analisis, tab_mineria, tab_inventario, tab_simulacion, tab_detalle = st.tabs([
    "📊 Dashboard",
    "📈 Análisis",
    "🧠 Minería de Datos",
    "📋 Inventario",
    "🧪 Simulación",
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


# ── TAB: Minería de Datos ───────────────────
with tab_mineria:
    st.subheader("🧠 Minería de Datos para Decisiones")
    st.caption(
        "Identifica patrones, entrena modelos predictivos, segmenta entidades y descubre reglas de asociación "
        "sobre el dataset filtrado actual."
    )

    if df_filtered.empty:
        st.warning("No hay datos para analizar con los filtros actuales.")
    else:
        cleaned_df, quality_report = clean_and_prepare_data(df_filtered)

        st.markdown("#### 1) Calidad de Datos (Limpieza y Transformación)")
        st.caption(
            "Qué es: diagnóstico de calidad del dataset. Cómo interpretarlo: observa cuánto se corrige antes de modelar para estimaciones más confiables."
        )
        qcol1, qcol2, qcol3, qcol4 = st.columns(4)
        with qcol1:
            st.metric(
                "Registros antes",
                quality_report["rows_before"],
                help="Qué es: cantidad original de filas antes de limpiar. Cómo interpretarlo: es tu base inicial para comparar impacto del proceso de calidad.",
            )
            st.caption("Qué es: volumen original de datos. Cómo interpretarlo: sirve como referencia de cobertura inicial.")
        with qcol2:
            st.metric(
                "Registros después",
                quality_report["rows_after"],
                help="Qué es: filas válidas tras limpieza y control de outliers. Cómo interpretarlo: si baja mucho, revisa filtros o reglas de depuración.",
            )
            st.caption("Qué es: volumen usable de datos. Cómo interpretarlo: refleja la base final para análisis y modelos.")
        with qcol3:
            st.metric(
                "Outliers removidos",
                quality_report["rows_removed_outliers"],
                help="Qué es: filas descartadas por valores atípicos (IQR). Cómo interpretarlo: niveles altos pueden indicar calidad irregular del origen.",
            )
            st.caption("Qué es: anomalías excluidas. Cómo interpretarlo: reduce ruido y sesgo en patrones/modelos.")
        with qcol4:
            st.metric(
                "Nulos corregidos",
                quality_report["missing_before"] - quality_report["missing_after"],
                help="Qué es: cantidad de valores faltantes imputados. Cómo interpretarlo: más correcciones implican mayor dependencia de supuestos estadísticos.",
            )
            st.caption("Qué es: faltantes completados. Cómo interpretarlo: mejora continuidad del análisis pero conviene monitorear su magnitud.")
        st.caption(
            "Se imputan nulos (mediana/moda) y se eliminan outliers con método IQR para mejorar precisión analítica."
        )

        st.divider()
        st.markdown("#### 2) Patrones de Comportamiento")
        st.caption(
            "Qué es: hallazgos descriptivos recurrentes del inventario. Cómo interpretarlo: prioriza combinaciones o variables con mayor frecuencia y consistencia."
        )
        patterns = identify_behavior_patterns(cleaned_df)

        if "patrones_frecuentes" in patterns:
            st.markdown("**Patrones frecuentes por marca/estado/transmisión**")
            st.dataframe(patterns["patrones_frecuentes"], use_container_width=True)
            st.caption("Qué es: combinaciones más repetidas. Cómo interpretarlo: mayor conteo sugiere foco comercial/operativo prioritario.")

        col_pat1, col_pat2 = st.columns(2)
        with col_pat1:
            if "tasa_venta_por_marca" in patterns:
                st.markdown("**Tasa de venta por marca**")
                tasa_df = patterns["tasa_venta_por_marca"].copy().head(15)
                if "tasa_venta" in tasa_df.columns:
                    tasa_df["tasa_venta"] = (tasa_df["tasa_venta"] * 100).round(2).astype(str) + "%"
                if "precio_promedio" in tasa_df.columns:
                    tasa_df["precio_promedio"] = tasa_df["precio_promedio"].round(0)
                st.dataframe(tasa_df, use_container_width=True)
                st.caption("Qué es: proporción histórica vendida por marca. Cómo interpretarlo: marcas con mayor tasa suelen rotar mejor.")

        with col_pat2:
            if "correlaciones_relevantes" in patterns:
                st.markdown("**Correlaciones numéricas más fuertes**")
                corr_df = patterns["correlaciones_relevantes"].copy()
                if "correlacion" in corr_df.columns:
                    corr_df["correlacion"] = corr_df["correlacion"].round(3)
                st.dataframe(corr_df[["variable_a", "variable_b", "correlacion"]], use_container_width=True)
                st.caption("Qué es: relación lineal entre variables numéricas. Cómo interpretarlo: cerca de 1/-1 es relación fuerte; cerca de 0, débil.")

        st.divider()
        st.markdown("#### 3) Modelos Predictivos (Regresión y Árboles)")
        st.caption(
            "Qué es: estimación de precio con algoritmos supervisados. Cómo interpretarlo: compara R² y MAE para elegir el modelo más útil."
        )
        if st.button(
            "Entrenar modelos predictivos",
            key="run_predictive_models",
            use_container_width=True,
            help="Qué es: ejecución del entrenamiento de regresión lineal y árbol. Cómo interpretarlo: actualiza métricas de desempeño con el dataset filtrado actual.",
        ):
            model_results = train_predictive_models(cleaned_df)
            if model_results.get("status") == "ok":
                model_metrics = model_results["metrics"].copy()
                model_metrics["r2"] = model_metrics["r2"].round(4)
                model_metrics["mae"] = model_metrics["mae"].apply(format_currency)

                st.success(
                    f"Modelos entrenados con {model_results['rows_train']} registros de entrenamiento "
                    f"y {model_results['rows_test']} de prueba."
                )
                st.dataframe(model_metrics, use_container_width=True)
                st.caption("Qué es: resumen de desempeño por modelo. Cómo interpretarlo: mayor R² y menor MAE indican mejor ajuste.")
                st.markdown("**Muestra de predicciones de precio**")
                pred_df = model_results["sample_predictions"].copy()
                for col in ["precio_real", "pred_regresion", "pred_arbol"]:
                    pred_df[col] = pred_df[col].apply(format_currency)
                st.dataframe(pred_df, use_container_width=True)
                st.caption("Qué es: comparación caso a caso entre valor real y predicho. Cómo interpretarlo: brechas grandes señalan segmentos difíciles de modelar.")
            else:
                st.warning(model_results.get("message", "No fue posible entrenar modelos con los datos actuales."))

        st.divider()
        st.markdown("#### 4) Segmentación de Entidades (Clustering)")
        st.caption(
            "Qué es: agrupación no supervisada por similitud. Cómo interpretarlo: cada segmento sugiere estrategias diferenciadas de precio y rotación."
        )
        n_clusters = st.slider(
            "Número de segmentos",
            min_value=2,
            max_value=7,
            value=4,
            step=1,
            help="Qué es: cantidad de grupos KMeans a formar. Cómo interpretarlo: más segmentos capturan detalle, pero pueden perder claridad de negocio.",
        )
        if st.button(
            "Ejecutar segmentación",
            key="run_segmentation",
            use_container_width=True,
            help="Qué es: ejecución del algoritmo de clustering. Cómo interpretarlo: genera perfiles promedio para diseñar decisiones por grupo.",
        ):
            segmentation = segment_entities(cleaned_df, n_clusters=int(n_clusters))
            if segmentation.get("status") == "ok":
                st.success(
                    "Segmentación completada. "
                    f"Variables usadas: {', '.join(segmentation['features'])}."
                )
                profile = segmentation["profile"].copy()
                if "precio_promedio" in profile.columns:
                    profile["precio_promedio"] = profile["precio_promedio"].apply(format_currency)
                if "km_promedio" in profile.columns:
                    profile["km_promedio"] = profile["km_promedio"].round(0)
                if "anio_promedio" in profile.columns:
                    profile["anio_promedio"] = profile["anio_promedio"].round(1)
                st.dataframe(profile, use_container_width=True)
                st.caption("Qué es: perfil agregado por segmento. Cómo interpretarlo: compara tamaño, precio y km para priorizar acciones por grupo.")
            else:
                st.warning(segmentation.get("message", "No fue posible ejecutar clustering."))

        st.divider()
        st.markdown("#### 5) Reglas de Asociación")
        st.caption(
            "Qué es: relaciones frecuentes entre atributos categóricos. Cómo interpretarlo: reglas con alta confianza y lift>1 son más accionables."
        )
        col_rule1, col_rule2 = st.columns(2)
        with col_rule1:
            min_support = st.slider(
                "Soporte mínimo",
                min_value=0.01,
                max_value=0.30,
                value=0.05,
                step=0.01,
                help="Qué es: frecuencia mínima de la regla en el dataset. Cómo interpretarlo: soporte alto exige reglas más comunes.",
            )
            st.caption("Qué es: proporción mínima de ocurrencia. Cómo interpretarlo: aumenta para reglas robustas, baja para descubrir patrones raros.")
        with col_rule2:
            min_confidence = st.slider(
                "Confianza mínima",
                min_value=0.10,
                max_value=0.95,
                value=0.35,
                step=0.05,
                help="Qué es: probabilidad de que ocurra el consecuente dado el antecedente. Cómo interpretarlo: valores altos implican reglas más confiables.",
            )
            st.caption("Qué es: fuerza condicional de la regla. Cómo interpretarlo: sube este umbral para quedarte con reglas más precisas.")

        if st.button(
            "Generar reglas de asociación",
            key="run_association_rules",
            use_container_width=True,
            help="Qué es: cálculo de reglas A -> B con soporte, confianza y lift. Cómo interpretarlo: filtra relaciones útiles para decisión comercial.",
        ):
            rules_df = generate_association_rules(
                cleaned_df,
                min_support=float(min_support),
                min_confidence=float(min_confidence),
                top_n=20,
            )

            if rules_df.empty:
                st.warning("No se encontraron reglas con los umbrales seleccionados.")
            else:
                show_rules = rules_df.copy()
                show_rules["soporte"] = (show_rules["soporte"] * 100).round(2).astype(str) + "%"
                show_rules["confianza"] = (show_rules["confianza"] * 100).round(2).astype(str) + "%"
                show_rules["lift"] = show_rules["lift"].round(3)
                st.dataframe(show_rules, use_container_width=True)
                st.caption("Qué es: ranking de reglas de co-ocurrencia. Cómo interpretarlo: lift>1 indica asociación positiva; lift≈1 sugiere independencia.")


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


# ── TAB: Simulación ─────────────────────────
with tab_simulacion:
    st.subheader("🧪 Simulación y Modelado de Decisiones")
    st.caption(
        "Evalúa escenarios determinísticos y estocásticos, valida el modelo con datos históricos "
        "y obtiene decisiones recomendadas por optimización."
    )

    if df_filtered.empty:
        st.warning("No hay datos con los filtros actuales para ejecutar simulaciones.")
    else:
        st.markdown("#### Alcance de la simulación")
        st.caption(
            "Define qué universo de vehículos se usa para proyectar ventas e ingresos. "
            "Cambiar este alcance modifica directamente la base de unidades y valor inicial."
        )
        use_available_only = False
        if "estado" in df_filtered.columns:
            use_available_only = st.checkbox(
                "Usar solo vehículos disponibles para simular",
                value=True,
                key="sim_only_available",
                help="Qué es: filtro del universo de simulación. Cómo interpretarlo: activado modela solo inventario disponible; desactivado incluye todos los estados filtrados.",
            )

        simulation_df = df_filtered.copy()
        if use_available_only and "estado" in simulation_df.columns:
            simulation_df = simulation_df[simulation_df["estado"].astype(str).str.lower() == "disponible"]

        total_sim_vehicles = len(simulation_df)
        avg_sim_price = (
            float(simulation_df["precio_cop"].dropna().mean())
            if "precio_cop" in simulation_df.columns and total_sim_vehicles > 0
            else 0.0
        )
        total_sim_value = (
            float(simulation_df["precio_cop"].dropna().sum())
            if "precio_cop" in simulation_df.columns and total_sim_vehicles > 0
            else 0.0
        )

        ctx_col1, ctx_col2, ctx_col3 = st.columns(3)
        with ctx_col1:
            st.metric("Vehículos para simular", total_sim_vehicles)
        with ctx_col2:
            st.metric("Valor promedio (base)", format_currency(avg_sim_price))
        with ctx_col3:
            st.metric("Valor total (base)", format_currency(total_sim_value))

        if simulation_df.empty:
            st.warning(
                "No hay vehículos en el alcance seleccionado para simular. "
                "Ajusta filtros o desactiva la opción de solo disponibles."
            )
        else:
            st.markdown("#### Variables de decisión")
            st.caption(
                "Son palancas internas que puedes controlar. Modifican precio esperado, volumen de ventas "
                "y costos asociados por unidad."
            )
            col_dec1, col_dec2, col_dec3 = st.columns(3)

            with col_dec1:
                discount_pct = st.slider(
                    "Descuento comercial (%)",
                    0,
                    20,
                    6,
                    key="sim_discount",
                    help="Qué es: porcentaje de rebaja sobre el precio comercial. Cómo interpretarlo: valores altos suelen impulsar ventas, pero reducen margen por unidad.",
                )
                st.caption("Qué es: ajuste del precio comercial. Cómo interpretarlo: más descuento suele vender más, pero reduce margen por unidad.")
            with col_dec2:
                reconditioning_mcop = st.slider(
                    "Reacondicionamiento (Millones COP/vehículo)",
                    0.0,
                    3.0,
                    1.0,
                    0.1,
                    key="sim_reconditioning",
                    help="Qué es: inversión media de preparación por vehículo. Cómo interpretarlo: valores altos elevan costo directo y exigen más volumen/margen para compensar.",
                )
                st.caption("Qué es: costo de preparación por vehículo. Cómo interpretarlo: mayor inversión puede sostener demanda, pero sube costos directos.")
            with col_dec3:
                model_type = st.radio(
                    "Tipo de simulación",
                    options=["Determinística", "Estocástica"],
                    horizontal=False,
                    key="sim_model_type",
                    help="Qué es: método de simulación a utilizar. Cómo interpretarlo: determinística entrega una estimación puntual; estocástica muestra distribución y riesgo.",
                )
                st.caption("Qué es: enfoque de cálculo del escenario. Cómo interpretarlo: determinística da un valor único; estocástica muestra rango y riesgo.")

            st.markdown("#### Variables externas")
            st.caption(
                "Factores del entorno que no controlas directamente. Afectan demanda, precios y costos regulatorios."
            )
            col_ext1, col_ext2, col_ext3 = st.columns(3)
            with col_ext1:
                market_change_pct = st.slider(
                    "Cambio del mercado (%)",
                    -20,
                    20,
                    3,
                    key="sim_market_change",
                    help="Qué es: cambio esperado del entorno de mercado. Cómo interpretarlo: positivo favorece demanda/precios; negativo los presiona a la baja.",
                )
                st.caption("Qué es: variación esperada del entorno comercial. Cómo interpretarlo: positivo favorece ventas/precios; negativo los presiona.")
            with col_ext2:
                regulation_cost_pct = st.slider(
                    "Costo por regulación (%)",
                    0,
                    20,
                    2,
                    key="sim_regulation",
                    help="Qué es: carga regulatoria adicional sobre la operación. Cómo interpretarlo: mayor porcentaje descuenta más utilidad sobre los ingresos.",
                )
                st.caption("Qué es: carga regulatoria sobre ingresos. Cómo interpretarlo: a mayor porcentaje, menor utilidad neta esperada.")
            with col_ext3:
                crisis_impact_pct = st.slider(
                    "Impacto crisis en demanda (%)",
                    0,
                    50,
                    8,
                    key="sim_crisis",
                    help="Qué es: intensidad del shock de crisis en demanda. Cómo interpretarlo: valores altos reducen conversiones y unidades vendidas esperadas.",
                )
                st.caption("Qué es: choque negativo de demanda. Cómo interpretarlo: valores altos reducen ritmo de ventas esperado.")

            n_simulations = 500
            if model_type == "Estocástica":
                n_simulations = st.slider(
                    "Número de simulaciones Monte Carlo",
                    200,
                    3000,
                    800,
                    100,
                    help="Qué es: número de iteraciones Monte Carlo. Cómo interpretarlo: más iteraciones mejoran estabilidad estadística, pero tardan más en ejecutar.",
                )
                st.caption("Qué es: número de corridas aleatorias. Cómo interpretarlo: más corridas mejora estabilidad estadística y aumenta tiempo de cálculo.")

            deterministic = simulate_deterministic(
                df=simulation_df,
                discount_pct=float(discount_pct),
                reconditioning_cost_mcop=float(reconditioning_mcop),
                market_change_pct=float(market_change_pct),
                regulation_cost_pct=float(regulation_cost_pct),
                crisis_impact_pct=float(crisis_impact_pct),
                reference_df=df_filtered,
            )

            st.markdown("#### Resultado del escenario")
            st.caption(
                "Resumen operativo y financiero del escenario seleccionado. Úsalo para comparar alternativas."
            )
            res_col1, res_col2, res_col3, res_col4 = st.columns(4)
            with res_col1:
                st.metric("Unidades vendidas esperadas", f"{deterministic['units_sold']:.0f}")
                st.caption("Qué es: cantidad estimada de unidades vendidas. Cómo interpretarlo: mayor valor implica mejor rotación del inventario.")
            with res_col2:
                st.metric("Ingreso esperado", format_currency(deterministic["revenue"]))
                st.caption("Qué es: ingresos brutos proyectados. Cómo interpretarlo: compáralo con utilidad para evaluar eficiencia del escenario.")
            with res_col3:
                st.metric("Utilidad esperada", format_currency(deterministic["expected_profit"]))
                st.caption("Qué es: ganancia neta estimada del escenario. Cómo interpretarlo: positivo indica rentabilidad; negativo alerta pérdidas potenciales.")
            with res_col4:
                st.metric("Unidades no vendidas", f"{deterministic['unsold_units']:.0f}")
                st.caption("Qué es: unidades que no se venderían en el escenario. Cómo interpretarlo: valores altos implican capital inmovilizado y menor rotación.")

            if model_type == "Estocástica":
                stochastic = simulate_stochastic(
                    df=simulation_df,
                    discount_pct=float(discount_pct),
                    reconditioning_cost_mcop=float(reconditioning_mcop),
                    market_change_pct=float(market_change_pct),
                    regulation_cost_pct=float(regulation_cost_pct),
                    crisis_impact_pct=float(crisis_impact_pct),
                    reference_df=df_filtered,
                    n_simulations=int(n_simulations),
                )

                st.markdown("#### Riesgo del escenario (Monte Carlo)")
                st.caption(
                    "Mide variabilidad de resultados cuando hay incertidumbre en el entorno y la demanda."
                )
                risk_col1, risk_col2, risk_col3, risk_col4 = st.columns(4)
                with risk_col1:
                    st.metric(
                        "Utilidad media",
                        format_currency(stochastic["profit_mean"]),
                        help="Qué es: media de utilidad en todas las simulaciones. Cómo interpretarlo: representa el resultado esperado central bajo incertidumbre.",
                    )
                    st.caption("Qué es: promedio de utilidades simuladas. Cómo interpretarlo: referencia central del resultado esperado bajo incertidumbre.")
                with risk_col2:
                    st.metric(
                        "Riesgo (desv. estándar)",
                        format_currency(stochastic["profit_std"]),
                        help="Qué es: dispersión de la utilidad simulada (desviación estándar). Cómo interpretarlo: valores altos implican mayor volatilidad y riesgo.",
                    )
                    st.caption("Qué es: variabilidad de la utilidad simulada. Cómo interpretarlo: más alto significa mayor volatilidad y riesgo.")
                with risk_col3:
                    st.metric(
                        "P10 utilidad",
                        format_currency(stochastic["profit_p10"]),
                        help="Qué es: percentil 10 de la utilidad simulada. Cómo interpretarlo: aproxima un escenario adverso; en 90% de corridas se obtiene un valor mayor.",
                    )
                    st.caption("Qué es: umbral bajo de utilidad (percentil 10). Cómo interpretarlo: sirve para evaluar escenarios adversos razonables.")
                with risk_col4:
                    st.metric(
                        "P90 utilidad",
                        format_currency(stochastic["profit_p90"]),
                        help="Qué es: percentil 90 de la utilidad simulada. Cómo interpretarlo: aproxima un escenario favorable; solo 10% de corridas lo superan.",
                    )
                    st.caption("Qué es: umbral alto de utilidad (percentil 90). Cómo interpretarlo: aproxima el potencial en escenarios favorables.")

            st.divider()
            st.markdown("#### Validación del modelo")
            st.caption(
                "Compara predicción base del modelo contra datos observados para evaluar precisión."
            )
            validation = validate_model(simulation_df, reference_df=df_filtered)
            val_col1, val_col2, val_col3, val_col4 = st.columns(4)
            with val_col1:
                st.metric(
                    "MAE unidades",
                    f"{validation['units_mae']:.2f}",
                    help="Qué es: error absoluto medio en unidades (MAE). Cómo interpretarlo: cuanto menor sea, más cerca está la predicción del histórico.",
                )
                st.caption("Qué es: error medio en unidades frente al histórico. Cómo interpretarlo: menor valor indica mejor precisión del modelo.")
            with val_col2:
                st.metric(
                    "MAPE unidades",
                    f"{validation['units_mape']:.2f}%",
                    help="Qué es: error porcentual medio en unidades (MAPE). Cómo interpretarlo: valores bajos indican mejor precisión relativa entre escenarios.",
                )
                st.caption("Qué es: error porcentual medio en unidades. Cómo interpretarlo: útil para comparar precisión entre distintos tamaños de muestra.")
            with val_col3:
                st.metric(
                    "MAE precio",
                    format_currency(validation["price_mae"]),
                    help="Qué es: error absoluto medio del precio (MAE). Cómo interpretarlo: valores bajos reflejan mejor ajuste del precio estimado.",
                )
                st.caption("Qué es: diferencia media en precio respecto al observado. Cómo interpretarlo: menor valor sugiere mejor calibración de precio.")
            with val_col4:
                st.metric(
                    "MAPE precio",
                    f"{validation['price_mape']:.2f}%",
                    help="Qué es: error porcentual medio del precio (MAPE). Cómo interpretarlo: cuanto menor sea, mayor confiabilidad en la calibración de precio.",
                )
                st.caption("Qué es: error porcentual medio del precio. Cómo interpretarlo: valores bajos indican ajuste más confiable del modelo.")
            st.caption(
                "La validación compara predicciones base vs métricas observadas del dataset seleccionado "
                "para la simulación."
            )

            st.divider()
            st.markdown("#### Optimización de políticas")
            st.caption(
                "Evalúa combinaciones de descuento y reacondicionamiento para maximizar utilidad "
                "ajustada por riesgo."
            )
            risk_aversion = st.slider(
                "Aversión al riesgo",
                min_value=0.0,
                max_value=1.0,
                value=0.25,
                step=0.05,
                help="Qué es: peso de penalización al riesgo en la optimización. Cómo interpretarlo: 0 prioriza retorno esperado; 1 prioriza estabilidad y menor volatilidad.",
            )
            st.caption("Qué es: peso que penaliza volatilidad en la optimización. Cómo interpretarlo: valores altos priorizan estabilidad sobre retorno máximo.")

            if st.button("Ejecutar optimización", key="run_optimization", use_container_width=True):
                optimization = optimize_decision(
                    df=simulation_df,
                    market_change_pct=float(market_change_pct),
                    regulation_cost_pct=float(regulation_cost_pct),
                    crisis_impact_pct=float(crisis_impact_pct),
                    reference_df=df_filtered,
                    risk_aversion=float(risk_aversion),
                    n_simulations=300,
                )
                best = optimization["best_decision"]
                st.success(
                    "Mejor combinación encontrada: "
                    f"descuento {best['discount_pct']:.1f}% y reacondicionamiento {best['reconditioning_mcop']:.1f}M COP."
                )
                best_col1, best_col2, best_col3 = st.columns(3)
                with best_col1:
                    st.metric("Utilidad media", format_currency(best["profit_mean"]))
                with best_col2:
                    st.metric("Riesgo", format_currency(best["profit_std"]))
                with best_col3:
                    st.metric("Puntaje utilidad-riesgo", f"{best['utility_score']:,.0f}")

                ranking = optimization["ranking"].copy().head(10)
                ranking["profit_mean"] = ranking["profit_mean"].apply(format_currency)
                ranking["profit_std"] = ranking["profit_std"].apply(format_currency)
                ranking["utility_score"] = ranking["utility_score"].map(lambda x: f"{x:,.0f}")
                st.dataframe(ranking, use_container_width=True)

            st.divider()
            st.markdown("#### Decisiones estratégicas sugeridas")
            st.caption(
                "Compara estrategias predefinidas y su balance entre retorno esperado y riesgo."
            )
            if st.button("Generar recomendación de estrategia", key="run_decision_reco", use_container_width=True):
                recommendations = generate_decision_recommendations(
                    df=simulation_df,
                    market_change_pct=float(market_change_pct),
                    regulation_cost_pct=float(regulation_cost_pct),
                    crisis_impact_pct=float(crisis_impact_pct),
                    reference_df=df_filtered,
                    n_simulations=400,
                )
                top_strategy = recommendations.iloc[0]["estrategia"]
                st.success(f"Estrategia recomendada: {top_strategy}")

                recommendations_display = recommendations.copy()
                for col in ["utilidad_esperada", "riesgo_std", "p10_utilidad", "p90_utilidad"]:
                    recommendations_display[col] = recommendations_display[col].apply(format_currency)
                recommendations_display["puntaje_decision"] = recommendations_display["puntaje_decision"].map(
                    lambda x: f"{x:,.0f}"
                )
                st.dataframe(recommendations_display, use_container_width=True)


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
