"""
Configuración centralizada de la aplicación DriveAnalytics
============================================================
Modifica este archivo para personalizar la aplicación.
"""

from pathlib import Path

# ─────────────────────────────────────────────
# RUTAS DE ARCHIVOS
# ─────────────────────────────────────────────
BASE_DIR = Path(__file__).parent.parent
DATA_FILE = BASE_DIR / "inventario_limpio.csv"

# ─────────────────────────────────────────────
# CONFIGURACIÓN DE LA APP
# ─────────────────────────────────────────────
APP_CONFIG = {
    "title": "🚗 DriveAnalytics",
    "subtitle": "Dashboard de Inventario - Concesionario",
    "page_icon": "🚗",
    "layout": "wide",
}

# ─────────────────────────────────────────────
# PALETA DE COLORES
# ─────────────────────────────────────────────
COLORS = {
    "primary": "#1f77b4",
    "secondary": "#ff7f0e",
    "success": "#2ca02c",
    "danger": "#d62728",
    "warning": "#ffbb33",
    "info": "#17becf",
    "background": "#0e1117",
    "card_bg": "#262730",
}

# Colores para gráficos (secuencia)
CHART_COLORS = [
    "#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", 
    "#9467bd", "#8c564b", "#e377c2", "#7f7f7f",
    "#bcbd22", "#17becf"
]

# ─────────────────────────────────────────────
# MAPEO DE COLUMNAS (para traducciones/etiquetas)
# ─────────────────────────────────────────────
COLUMN_LABELS = {
    "marca": "Marca",
    "modelo": "Modelo",
    "año": "Año",
    "estado": "Estado",
    "kilometraje": "Kilometraje",
    "motor": "Motor (L)",
    "placa": "Placa",
    "cv": "Potencia (CV)",
    "peso_kg": "Peso (kg)",
    "transmisión": "Transmisión",
    "precio_cop": "Precio (COP)",
}

# ─────────────────────────────────────────────
# CONFIGURACIÓN DE ESTADOS
# ─────────────────────────────────────────────
ESTADO_CONFIG = {
    "disponible": {"color": "#2ca02c", "icon": "✅", "label": "Disponible"},
    "vendido": {"color": "#1f77b4", "icon": "💰", "label": "Vendido"},
    "taller": {"color": "#ff7f0e", "icon": "🔧", "label": "En Taller"},
}

# ─────────────────────────────────────────────
# FILTROS DISPONIBLES
# ─────────────────────────────────────────────
FILTERABLE_COLUMNS = ["marca", "estado", "transmisión", "año"]

# ─────────────────────────────────────────────
# CONFIGURACIÓN DE GRÁFICOS
# ─────────────────────────────────────────────
CHART_CONFIG = {
    "height": 400,
    "use_container_width": True,
}

# ─────────────────────────────────────────────
# FORMATO DE NÚMEROS
# ─────────────────────────────────────────────
def format_currency(value: float) -> str:
    """Formatea valor como moneda colombiana."""
    return f"${value:,.0f} COP".replace(",", ".")


def format_km(value: float) -> str:
    """Formatea kilometraje."""
    return f"{value:,.0f} km".replace(",", ".")
