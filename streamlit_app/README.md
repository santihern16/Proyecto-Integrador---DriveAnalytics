# 🚗 DriveAnalytics - Dashboard de Inventario

Dashboard interactivo para visualización y análisis de datos de inventario de un concesionario de autos.

## 📁 Estructura del Proyecto

```
streamlit_app/
├── app.py                  # Aplicación principal
├── config.py               # Configuración centralizada
├── requirements.txt        # Dependencias
├── components/             # Componentes reutilizables
│   ├── __init__.py
│   ├── charts.py          # Gráficos con Plotly
│   ├── data_table.py      # Tablas y tarjetas de datos
│   ├── filters.py         # Filtros del sidebar
│   └── kpi_cards.py       # Tarjetas de métricas
└── utils/                  # Utilidades
    ├── __init__.py
    ├── data_loader.py     # Carga y filtrado de datos
    └── metrics.py         # Cálculo de KPIs
```

## 🚀 Instalación y Ejecución

### 1. Instalar dependencias

```bash
pip install -r streamlit_app/requirements.txt
```

### 2. Ejecutar la aplicación

```bash
streamlit run streamlit_app/app.py
```

La aplicación se abrirá en `http://localhost:8501`

## 📊 Funcionalidades

### Dashboard Principal
- **KPIs en tiempo real**: Total de vehículos, disponibles, vendidos, en taller
- **Métricas financieras**: Valor del inventario, precio promedio, km promedio

### Visualizaciones
- Distribución por estado (gráfico de dona)
- Vehículos por marca (barras horizontales)
- Precio promedio por año (línea temporal)
- Relación kilometraje vs precio (scatter plot)
- Distribución de precios por marca (box plot)

### Filtros
- Por marca (multiselect)
- Por estado (multiselect)
- Por transmisión (multiselect)
- Por rango de año (slider)
- Por rango de precio (slider)
- Por rango de kilometraje (slider)

### Inventario
- Vista en tabla interactiva
- Vista en tarjetas
- Exportación a CSV
- Selección de columnas

### Búsqueda de Vehículos
- Búsqueda por placa
- Búsqueda por modelo
- Vista detallada del vehículo

## 🛠️ Personalización

### Agregar nuevas columnas
1. Actualiza `COLUMN_LABELS` en `config.py` con la etiqueta de la nueva columna
2. Si es filtrable, agrégala a `FILTERABLE_COLUMNS`

### Agregar nuevos gráficos
1. Crea una función en `components/charts.py`
2. Importa y usa la función en `app.py`

### Modificar estilos
- Colores: Ajusta `COLORS` y `CHART_COLORS` en `config.py`
- CSS: Modifica el bloque `<style>` en `app.py`

### Agregar nuevas páginas (multipágina)
Streamlit soporta estructura multipágina. Crea una carpeta `pages/` dentro de `streamlit_app/`:

```
streamlit_app/
├── app.py
└── pages/
    ├── 1_📊_Reportes.py
    └── 2_⚙️_Configuracion.py
```

## 📝 Notas

- Los datos se cargan desde `inventario_limpio.csv` (generado por el ETL)
- El caché de datos se actualiza cada 5 minutos
- La aplicación usa tema oscuro por defecto

## 🔧 Requisitos del Sistema

- Python 3.8+
- Navegador web moderno
