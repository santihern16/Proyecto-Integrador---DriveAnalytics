# DriveAnalytics

Dashboard interactivo para analizar inventario de vehiculos de un concesionario con Streamlit.

## Requisitos

- Python 3.10 o superior
- pip
- Git (para subir a GitHub)

## Estructura principal

- `streamlit_app/app.py`: punto de entrada de la aplicacion
- `streamlit_app/requirements.txt`: dependencias de Python
- `inventario_limpio.csv`: dataset usado por defecto

## 1) Clonar el repositorio

```bash
git clone https://github.com/TU_USUARIO/TU_REPOSITORIO.git
cd TU_REPOSITORIO
```

## 2) Crear y activar entorno virtual

### macOS / Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### Windows (PowerShell)

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

## 3) Instalar dependencias

```bash
pip install --upgrade pip
pip install -r streamlit_app/requirements.txt
```

## 4) Verificar que exista el dataset

La aplicacion carga por defecto el archivo:

- `inventario_limpio.csv`

Si no existe, agrega ese archivo en la raiz del proyecto.

## 5) Ejecutar la aplicacion

```bash
streamlit run streamlit_app/app.py
```

Abrir en el navegador:

- http://localhost:8501

## 6) Subir el proyecto a GitHub

Si es la primera vez que lo subes:

```bash
git init
git add .
git commit -m "feat: version inicial de DriveAnalytics"
git branch -M main
git remote add origin https://github.com/TU_USUARIO/TU_REPOSITORIO.git
git push -u origin main
```

Si el repositorio ya existe y solo quieres actualizar cambios:

```bash
git add .
git commit -m "docs: actualizar README"
git push
```

## Comandos utiles

Ejecutar Streamlit en otro puerto:

```bash
streamlit run streamlit_app/app.py --server.port 8502
```

Detener la app en terminal:

- `Ctrl + C`

## Notas

- El dataset configurado en la app se define en `streamlit_app/config.py` en la variable `DATA_FILE`.
- Si cambias el nombre o ruta del CSV, actualiza esa variable.
