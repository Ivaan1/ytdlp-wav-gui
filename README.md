# yt-dlp audio

Aplicación de escritorio para descargar el audio de vídeos de YouTube (WAV,
MP3, M4A o FLAC) pegando sus enlaces. Por debajo usa
[yt-dlp](https://github.com/yt-dlp/yt-dlp) y [ffmpeg](https://ffmpeg.org/).

## Instalación (Windows)

Solo hay que hacerlo una vez. Todos los comandos se escriben en **PowerShell**
(menú Inicio → escribe "PowerShell" → Enter).

### 1. Instala Python y ffmpeg

```powershell
winget install Python.Python.3.13
winget install Gyan.FFmpeg
```

Cierra PowerShell y ábrelo de nuevo para que reconozca los programas recién
instalados. Comprueba que funcionan:

```powershell
python --version
ffmpeg -version
```

> Si prefieres instalar Python desde [python.org](https://www.python.org/downloads/),
> marca la casilla **"Add python.exe to PATH"** durante la instalación.

### 2. Descarga el proyecto

Con Git:

```powershell
cd $HOME\Documents
git clone https://github.com/Ivaan1/ytdlp-wav-gui.git
cd ytdlp-wav-gui
```

O sin Git: en GitHub pulsa **Code → Download ZIP**, descomprímelo en una
carpeta fija (por ejemplo `Documentos\ytdlp-wav-gui`) y abre PowerShell en esa
carpeta (en el Explorador: clic derecho en un hueco vacío → **Abrir en
Terminal**).

> Elige una ubicación definitiva: el acceso directo apunta a esta carpeta. Si
> la mueves después, repite el paso 4.

### 3. Instala las dependencias

Dentro de la carpeta del proyecto:

```powershell
python -m venv .venv --upgrade-deps
.venv\Scripts\python.exe -m pip install -r requirements.txt
```

### 4. Crea el acceso directo

```powershell
powershell -ExecutionPolicy Bypass -File create_shortcut.ps1 -Desktop
```

Esto crea **yt-dlp audio** en el menú Inicio y en el escritorio (quita
`-Desktop` si solo lo quieres en el menú Inicio). Se abre como cualquier otra
aplicación, sin ventana de consola.

**Para anclarla a la barra de tareas:** abre el menú Inicio, busca
"yt-dlp audio", clic derecho → **Anclar a la barra de tareas**.

> Ánclala desde el menú Inicio, no desde el icono de la app abierta en la
> barra de tareas: así se anclaría Python en vez de la aplicación.

## Uso

1. Pega uno o varios enlaces de YouTube, uno por línea.
2. Elige la carpeta de destino (por defecto `Música\backing tracks`).
3. Elige **Formato** y **Calidad**:
   - **WAV / FLAC**: sin pérdida, ideal para editar o producir.
   - **MP3 / M4A**: archivos más ligeros. La calidad (Máxima → Baja) solo
     afecta a estos formatos.
   - **BEST**: deja el audio en el mejor formato original disponible.
4. Pulsa **Descargar**. El progreso aparece en la barra y en el registro.
   **Cancelar** detiene la cola.

### Opciones avanzadas

Pulsa **▸ Opciones avanzadas** para desplegarlas:

| Opción | Qué hace |
| --- | --- |
| Descargar playlist completa | Si el enlace es de una playlist, descarga todos sus vídeos en vez de solo uno. |
| Incrustar miniatura | Añade la portada del vídeo al archivo (no compatible con WAV). |
| Conservar vídeo original | No borra el vídeo descargado después de extraer el audio. |
| Añadir metadatos | Guarda título, artista, etc. dentro del archivo. Activada por defecto. |
| Plantilla de nombre | Nombre de los archivos con [variables de yt-dlp](https://github.com/yt-dlp/yt-dlp#output-template), p. ej. `%(artist)s - %(title)s.%(ext)s`. |

### Actualizar yt-dlp

YouTube cambia a menudo, y cuando lo hace las descargas dejan de funcionar
hasta que yt-dlp se actualiza. **Si una descarga falla sin motivo aparente,
pulsa ↻ Actualizar** (arriba a la derecha). Si hay versión nueva, la app
ofrece reiniciarse para usarla. Debajo del botón se ve la versión instalada.

## Problemas comunes

| Síntoma | Solución |
| --- | --- |
| `python` no se reconoce como comando | Cierra y vuelve a abrir PowerShell tras instalar Python. Si sigue igual, reinstálalo marcando "Add python.exe to PATH". |
| Error con `ffmpeg` / `ffprobe not found` | ffmpeg no está instalado o no está en el PATH. Repite el paso 1 y cierra sesión en Windows y vuelve a entrar. |
| `python -m venv` falla con un error de `ensurepip` | Borra la carpeta `.venv`, ejecuta `python -m pip install --upgrade pip` y repite el paso 3. |
| Las descargas fallan de repente | Pulsa **↻ Actualizar**. |
| El acceso directo ya no abre nada | Has movido la carpeta o borrado `.venv`. Repite los pasos 3 y 4. |

## Para desarrolladores

Arrancar desde la terminal (muestra errores en consola):

```powershell
.venv\Scripts\python.exe main.py
```

```
ytdlp-wav-gui/
├── main.py                 # punto de entrada
├── ytdlp_wav_gui/
│   ├── app.py              # interfaz Tkinter (tema, widgets, eventos)
│   └── downloader.py       # wrapper sobre la API de yt-dlp y su actualización
├── assets/icon.ico         # icono de la ventana y del acceso directo
├── create_shortcut.ps1     # crea el acceso directo de Windows
└── requirements.txt
```

- Los colores del tema están en `COLORS` al principio de `app.py`.
- Los audios descargados (`*.wav`, `*.mp3`, etc.) están excluidos del control
  de versiones vía `.gitignore`.
