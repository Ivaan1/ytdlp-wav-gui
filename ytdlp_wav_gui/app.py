from __future__ import annotations

import os
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext, ttk

from .downloader import DownloadOptions, Downloader

DEFAULT_OUTPUT_DIR = os.path.join(os.path.expanduser("~"), "Music", "backing tracks")
AUDIO_FORMATS = ["wav", "mp3", "m4a", "flac", "best"]
QUALITY_OPTIONS = ["0 (mejor)", "2", "5", "9 (peor)"]


class App(ttk.Frame):
    def __init__(self, master: tk.Tk):
        super().__init__(master, padding=12)
        self.master = master
        self.master.title("yt-dlp WAV GUI")
        self.master.geometry("720x580")
        self.pack(fill="both", expand=True)

        self._downloader: Downloader | None = None
        self._worker: threading.Thread | None = None

        self._build_widgets()

    def _build_widgets(self) -> None:
        ttk.Label(self, text="URLs de YouTube (una por línea):").pack(anchor="w")
        self.url_text = scrolledtext.ScrolledText(self, height=6)
        self.url_text.pack(fill="x", pady=(0, 10))

        out_frame = ttk.Frame(self)
        out_frame.pack(fill="x", pady=(0, 10))
        ttk.Label(out_frame, text="Carpeta de salida:").pack(side="left")
        self.output_var = tk.StringVar(value=DEFAULT_OUTPUT_DIR)
        ttk.Entry(out_frame, textvariable=self.output_var).pack(side="left", fill="x", expand=True, padx=6)
        ttk.Button(out_frame, text="Elegir...", command=self._choose_dir).pack(side="left")

        opts_frame = ttk.LabelFrame(self, text="Opciones de yt-dlp", padding=10)
        opts_frame.pack(fill="x", pady=(0, 10))

        ttk.Label(opts_frame, text="Formato de audio:").grid(row=0, column=0, sticky="w")
        self.format_var = tk.StringVar(value="wav")
        ttk.Combobox(
            opts_frame, textvariable=self.format_var, values=AUDIO_FORMATS, width=10, state="readonly"
        ).grid(row=0, column=1, sticky="w", padx=6)

        ttk.Label(opts_frame, text="Calidad audio:").grid(row=0, column=2, sticky="w", padx=(20, 0))
        self.quality_var = tk.StringVar(value=QUALITY_OPTIONS[0])
        ttk.Combobox(
            opts_frame, textvariable=self.quality_var, values=QUALITY_OPTIONS, width=12, state="readonly"
        ).grid(row=0, column=3, sticky="w", padx=6)

        ttk.Label(opts_frame, text="Plantilla de nombre:").grid(row=1, column=0, sticky="w", pady=(8, 0))
        self.template_var = tk.StringVar(value="%(title)s.%(ext)s")
        ttk.Entry(opts_frame, textvariable=self.template_var, width=30).grid(
            row=1, column=1, columnspan=3, sticky="we", padx=6, pady=(8, 0)
        )

        self.playlist_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(opts_frame, text="Descargar playlist completa", variable=self.playlist_var).grid(
            row=2, column=0, columnspan=2, sticky="w", pady=(8, 0)
        )

        self.thumbnail_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(opts_frame, text="Incrustar miniatura", variable=self.thumbnail_var).grid(
            row=2, column=2, columnspan=2, sticky="w", pady=(8, 0)
        )

        self.metadata_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(opts_frame, text="Añadir metadatos", variable=self.metadata_var).grid(
            row=3, column=0, columnspan=2, sticky="w"
        )

        self.keepvideo_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(opts_frame, text="Conservar vídeo original", variable=self.keepvideo_var).grid(
            row=3, column=2, columnspan=2, sticky="w"
        )

        opts_frame.columnconfigure(1, weight=1)
        opts_frame.columnconfigure(3, weight=1)

        btn_frame = ttk.Frame(self)
        btn_frame.pack(fill="x", pady=(0, 10))
        self.download_btn = ttk.Button(btn_frame, text="Descargar", command=self._start_download)
        self.download_btn.pack(side="left")
        self.cancel_btn = ttk.Button(btn_frame, text="Cancelar", command=self._cancel_download, state="disabled")
        self.cancel_btn.pack(side="left", padx=(8, 0))

        self.progress = ttk.Progressbar(self, mode="determinate", maximum=100)
        self.progress.pack(fill="x", pady=(0, 10))

        ttk.Label(self, text="Registro:").pack(anchor="w")
        self.log_text = scrolledtext.ScrolledText(self, height=12, state="disabled")
        self.log_text.pack(fill="both", expand=True)

    def _choose_dir(self) -> None:
        chosen = filedialog.askdirectory(initialdir=self.output_var.get() or os.getcwd())
        if chosen:
            self.output_var.set(chosen)

    def _log(self, message: str) -> None:
        def _append() -> None:
            self.log_text.configure(state="normal")
            self.log_text.insert("end", message.rstrip() + "\n")
            self.log_text.see("end")
            self.log_text.configure(state="disabled")

        self.master.after(0, _append)

    def _on_progress(self, data: dict) -> None:
        status = data.get("status")
        if status == "downloading":
            total = data.get("total_bytes") or data.get("total_bytes_estimate")
            downloaded = data.get("downloaded_bytes", 0)
            if total:
                pct = downloaded / total * 100
                self.master.after(0, lambda: self.progress.configure(value=pct))
        elif status == "finished":
            self.master.after(0, lambda: self.progress.configure(value=100))

    def _quality_value(self) -> str:
        return self.quality_var.get().split(" ")[0]

    def _start_download(self) -> None:
        urls = [u.strip() for u in self.url_text.get("1.0", "end").splitlines() if u.strip()]
        if not urls:
            messagebox.showwarning("Sin URLs", "Pega al menos una URL de YouTube.")
            return
        output_dir = self.output_var.get().strip()
        if not output_dir:
            messagebox.showwarning("Sin carpeta", "Elige una carpeta de salida.")
            return

        options = DownloadOptions(
            output_dir=output_dir,
            audio_format=self.format_var.get(),
            audio_quality=self._quality_value(),
            filename_template=self.template_var.get().strip() or "%(title)s.%(ext)s",
            download_playlist=self.playlist_var.get(),
            embed_thumbnail=self.thumbnail_var.get(),
            add_metadata=self.metadata_var.get(),
            keep_video=self.keepvideo_var.get(),
        )

        self._downloader = Downloader(self._log, self._on_progress)
        self.download_btn.configure(state="disabled")
        self.cancel_btn.configure(state="normal")
        self.progress.configure(value=0)

        def _run() -> None:
            try:
                self._downloader.download(urls, options)
            finally:
                self.master.after(0, self._on_finished)

        self._worker = threading.Thread(target=_run, daemon=True)
        self._worker.start()

    def _cancel_download(self) -> None:
        if self._downloader:
            self._downloader.cancel()
            self._log("Cancelando...")

    def _on_finished(self) -> None:
        self.download_btn.configure(state="normal")
        self.cancel_btn.configure(state="disabled")
        self._log("Proceso terminado.")


def main() -> None:
    root = tk.Tk()
    App(root)
    root.mainloop()


if __name__ == "__main__":
    main()
