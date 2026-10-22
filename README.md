# ytdlp-wav-gui

Interfaz de escritorio (Tkinter) para descargar audio de YouTube como WAV
usando [yt-dlp](https://github.com/yt-dlp/yt-dlp) como librería de Python.

## Requisitos

- Python 3.10+
- [ffmpeg](https://ffmpeg.org/) instalado y disponible en el `PATH` (necesario
  para que yt-dlp extraiga y convierta el audio).

## Instalación

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## Uso

```bash
python main.py
```

En la ventana:

1. Pega una o varias URLs de YouTube (una por línea).
2. Elige la carpeta de salida (por defecto `Music/backing tracks`).
3. Ajusta las opciones de yt-dlp:
   - **Formato de audio**: wav, mp3, m4a, flac o el mejor disponible.
   - **Calidad de audio**: calidad objetivo para el post-proceso de ffmpeg.
   - **Plantilla de nombre**: patrón de nombre de archivo de yt-dlp
     (por ejemplo `%(title)s.%(ext)s`).
   - **Descargar playlist completa**: si la URL es una playlist, descarga
     todos sus elementos en vez de solo el primero.
   - **Incrustar miniatura**: guarda y embebe la miniatura del vídeo.
   - **Añadir metadatos**: escribe metadatos (título, artista, etc.) en el
     archivo de audio resultante.
   - **Conservar vídeo original**: no borra el archivo de vídeo intermedio
     tras extraer el audio.
4. Pulsa **Descargar**. El progreso y los mensajes de yt-dlp aparecen en el
   registro inferior. **Cancelar** detiene la cola de descargas en curso.

## Estructura del proyecto

```
ytdlp-wav-gui/
├── main.py                  # punto de entrada
├── ytdlp_wav_gui/
│   ├── app.py                # interfaz Tkinter
│   └── downloader.py         # wrapper sobre la API de yt-dlp
├── requirements.txt
└── README.md
```

## Notas

- Este repositorio es privado por ahora.
- Los archivos de audio descargados (`*.wav`, `*.mp3`, etc.) están excluidos
  del control de versiones vía `.gitignore`.
