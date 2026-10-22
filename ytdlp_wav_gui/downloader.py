from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Callable

import yt_dlp


@dataclass
class DownloadOptions:
    output_dir: str
    audio_format: str = "wav"
    audio_quality: str = "0"
    filename_template: str = "%(title)s.%(ext)s"
    download_playlist: bool = False
    embed_thumbnail: bool = False
    add_metadata: bool = True
    keep_video: bool = False


class _YdlLogger:
    def __init__(self, log_callback: Callable[[str], None]):
        self._log = log_callback

    def debug(self, msg):
        if msg.startswith("[debug] "):
            return
        self._log(msg)

    def info(self, msg):
        self._log(msg)

    def warning(self, msg):
        self._log(f"AVISO: {msg}")

    def error(self, msg):
        self._log(f"ERROR: {msg}")


class Downloader:
    """Thin wrapper around yt-dlp's Python API, used by the GUI."""

    def __init__(self, log_callback: Callable[[str], None], progress_callback: Callable[[dict], None]):
        self._log = log_callback
        self._progress = progress_callback
        self._cancel_requested = False

    def cancel(self) -> None:
        self._cancel_requested = True

    def _hook(self, data: dict) -> None:
        if self._cancel_requested:
            raise yt_dlp.utils.DownloadCancelled("Cancelado por el usuario")
        self._progress(data)

    def _build_opts(self, options: DownloadOptions) -> dict:
        postprocessors = [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": options.audio_format,
                "preferredquality": options.audio_quality,
            }
        ]
        if options.add_metadata:
            postprocessors.append({"key": "FFmpegMetadata"})
        if options.embed_thumbnail:
            postprocessors.append({"key": "EmbedThumbnail"})

        outtmpl = os.path.join(options.output_dir, options.filename_template)

        return {
            "format": "bestaudio/best",
            "outtmpl": outtmpl,
            "noplaylist": not options.download_playlist,
            "postprocessors": postprocessors,
            "writethumbnail": options.embed_thumbnail,
            "keepvideo": options.keep_video,
            "progress_hooks": [self._hook],
            "logger": _YdlLogger(self._log),
            "quiet": True,
            "no_warnings": False,
        }

    def download(self, urls: list[str], options: DownloadOptions) -> None:
        self._cancel_requested = False
        os.makedirs(options.output_dir, exist_ok=True)
        ydl_opts = self._build_opts(options)

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            for url in urls:
                if self._cancel_requested:
                    self._log("Descarga cancelada.")
                    break
                self._log(f"Descargando: {url}")
                try:
                    ydl.download([url])
                except yt_dlp.utils.DownloadCancelled:
                    self._log("Descarga cancelada.")
                    break
                except Exception as exc:
                    self._log(f"Error con {url}: {exc}")
