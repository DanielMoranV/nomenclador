# Nomenclador Empresarial de Facturas

Aplicación de escritorio **portable y automatizada** diseñada para la lectura inteligente y el renombrado masivo de facturas en formato PDF, adaptada para procesos contables y administrativos de aseguradoras.

## Características Principales

- **Procesamiento Masivo:** Selecciona un directorio origen con múltiples PDFs y un destino para organizarlos automáticamente.
- **Lectura Híbrida Inteligente:**
  - Extrae el texto nativo directamente de documentos generados digitalmente.
  - Si el PDF es un documento escaneado (imagen), utiliza **Tesseract OCR** de forma automática para reconocer y leer el texto impreso.
- **Identificación Automática:** Emplea expresiones regulares avanzadas para detectar con precisión números de Serie y Correlativos de facturas ocultos en la estructura del documento.
- **Formatos por Aseguradora:** Guarda los archivos con las nomenclaturas exactas requeridas por diferentes entidades, seleccionables desde la interfaz:
  - **Rímac:** `20526109237_01_[SERIE]_[NUMERO].pdf`
  - **Pacífico:** `FA-[SERIE]-[NUMERO].pdf`
- **Instalador Integrado de OCR:** La interfaz detecta si tu equipo carece del motor Tesseract OCR (necesario para leer imágenes) e incluye un botón de **Autoinstalación Silenciosa** que lo descarga y configura por ti en un clic.
- **Portable:** Puedes compilar la aplicación en un archivo `.exe` único y llevarlo a cualquier ordenador con Windows sin necesidad de instalar Python.
- **Prevención de Errores:** Los documentos ilegibles o que no posean formato de factura son copiados de manera separada con el prefijo `ERROR_` para facilitar su revisión ocular humana.

## Tecnologías Utilizadas

- **Lenguaje:** Python 3.13+
- **Interfaz Gráfica:** Tkinter (GUI Nativa de Windows)
- **Lectura PDF:** `pypdf`
- **Reconocimiento Óptico de Caracteres (OCR):** `pytesseract` y binarios de Tesseract v5.4.
- **Manipulación de Imágenes:** `Pillow` (PIL)
- **Compilación:** `PyInstaller`

## Guía de Uso Rápido (.exe)

Si tienes el archivo compilado `nomenclador_app.exe` en tu carpeta `dist/`:

1.  Abre la aplicación haciendo doble clic en **`nomenclador_app.exe`**.
2.  Observa el estado del panel inferior **"Estado motor OCR"**. Si dice "Motor no instalado" en rojo, pulsa el botón naranja **"Instalar Tesseract"**. Espera a que el indicador cambie a "Activo y Funcionando" en verde. _(Solo es necesario hacerlo la primera vez en un ordenador nuevo)_.
3.  En la interfaz, haz clic en **"Examinar"** y elige tu **Directorio de Origen** (donde están todos los PDFs descargados y desordenados).
4.  Haz clic en el segundo botón **"Examinar"** y selecciona el **Directorio de Destino** (donde quieres que se guarden los PDFs ya renombrados).
5.  Despliega el menú de **Aseguradora** y selecciona la entidad para la cual vas a generar los archivos (ej. Rímac).
6.  Pulsa el botón azul **"INICIAR PROCESAMIENTO"**.
7.  Observa el progreso en la consola negra inferior. Verás en tiempo real qué documentos han sido procesados con éxito y guardados, y cuáles (si los hay) enviaron errores a revisión.

## Guía para Desarrolladores

Si deseas modificar el código o volver a compilar la aplicación, sigue estos pasos:

### 1. Preparar el Entorno

Asegúrate de tener instalado Python en tu sistema. Clona o descarga el proyecto.

Instala las dependencias necesarias abriendo tu consola web o terminal en la ruta principal del proyecto:

```bash
pip install pyinstaller Pillow pypdf pytesseract
```

### 2. Ejecutar el Script Directamente

Para probar el programa localmente sin compilar:

```bash
python nomenclador_app.py
```

### 3. Compilar el Archivo Portable (.exe)

Para generar un ejecutable final para su distribución sin dependencias, en entornos Windows:

```bash
pyinstaller --noconsole --onefile nomenclador_app.py
```

_(Nota: El archivo `.exe` final aparecerá dentro de la carpeta oculta `dist/` en tu proyecto)._

---

_Desarrollado para optimización de procesos contables._
