from __future__ import annotations

import os
import sys
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from tkinter import font as tkfont

from .downloader import DownloadOptions, Downloader

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ICON_PATH = os.path.join(PROJECT_ROOT, "assets", "icon.ico")
DEFAULT_OUTPUT_DIR = os.path.join(os.path.expanduser("~"), "Music", "backing tracks")
AUDIO_FORMATS = ["wav", "mp3", "m4a", "flac", "best"]
QUALITY_OPTIONS = [("Máxima", "0"), ("Alta", "2"), ("Media", "5"), ("Baja", "9")]

COLORS = {
    "bg": "#111315",
    "surface": "#1A1D21",
    "border": "#2A2E34",
    "text": "#ECEEF1",
    "muted": "#8A919B",
    "accent": "#FF6A3D",
    "accent_hover": "#FF8560",
    "on_accent": "#111315",
}

UI_FONTS = ["Segoe UI Variable Text", "Segoe UI", "Inter", "Helvetica Neue", "Helvetica"]
DISPLAY_FONTS = ["Segoe UI Variable Display", "Segoe UI Semibold", "Segoe UI", "Inter", "Helvetica Neue"]
MONO_FONTS = ["Cascadia Mono", "Cascadia Code", "JetBrains Mono", "Consolas", "Menlo"]


def _pick_font(root: tk.Misc, candidates: list[str], fallback: str) -> str:
    available = set(tkfont.families(root))
    return next((f for f in candidates if f in available), fallback)


class App(ttk.Frame):
    def __init__(self, master: tk.Tk):
        self.master = master
        self.master.title("yt-dlp audio")
        self.master.geometry("760x720")
        self.master.minsize(640, 560)
        self.master.configure(bg=COLORS["bg"])

        self.ui_font = _pick_font(master, UI_FONTS, "TkDefaultFont")
        self.display_font = _pick_font(master, DISPLAY_FONTS, self.ui_font)
        self.mono_font = _pick_font(master, MONO_FONTS, "TkFixedFont")
        self._setup_style()

        super().__init__(master, padding=(28, 24))
        self.pack(fill="both", expand=True)

        self._downloader: Downloader | None = None
        self._worker: threading.Thread | None = None
        self._advanced_open = False

        self._build_widgets()

    def _setup_style(self) -> None:
        c = COLORS
        tkfont.nametofont("TkDefaultFont").configure(family=self.ui_font, size=10)
        tkfont.nametofont("TkTextFont").configure(family=self.ui_font, size=10)

        style = ttk.Style(self.master)
        style.theme_use("clam")
        style.configure(
            ".",
            background=c["bg"],
            foreground=c["text"],
            fieldbackground=c["surface"],
            bordercolor=c["border"],
            lightcolor=c["border"],
            darkcolor=c["border"],
            troughcolor=c["surface"],
            focuscolor=c["bg"],
            selectbackground=c["accent"],
            selectforeground=c["on_accent"],
            font=(self.ui_font, 10),
        )

        style.configure("Title.TLabel", font=(self.display_font, 20, "bold"))
        style.configure("Muted.TLabel", foreground=c["muted"])
        style.configure("Section.TLabel", foreground=c["muted"], font=(self.ui_font, 8, "bold"))

        style.configure("TEntry", padding=(10, 7), insertcolor=c["text"])
        style.map("TEntry", bordercolor=[("focus", c["accent"])], lightcolor=[("focus", c["accent"])])

        style.configure(
            "Accent.TButton",
            background=c["accent"],
            foreground=c["on_accent"],
            bordercolor=c["accent"],
            lightcolor=c["accent"],
            darkcolor=c["accent"],
            padding=(22, 9),
            font=(self.ui_font, 10, "bold"),
        )
        style.map(
            "Accent.TButton",
            background=[("disabled", c["border"]), ("active", c["accent_hover"])],
            foreground=[("disabled", c["muted"])],
            bordercolor=[("disabled", c["border"]), ("active", c["accent_hover"])],
            lightcolor=[("disabled", c["border"]), ("active", c["accent_hover"])],
            darkcolor=[("disabled", c["border"]), ("active", c["accent_hover"])],
        )

        style.configure("Ghost.TButton", background=c["surface"], padding=(16, 9))
        style.map(
            "Ghost.TButton",
            background=[("disabled", c["bg"]), ("active", c["border"])],
            foreground=[("disabled", c["border"])],
        )

        style.configure("Link.TButton", background=c["bg"], foreground=c["muted"], borderwidth=0, padding=0)
        style.map("Link.TButton", background=[("active", c["bg"])], foreground=[("active", c["text"])])

        style.configure("Pill.Toolbutton", background=c["surface"], foreground=c["muted"], padding=(14, 6))
        style.map(
            "Pill.Toolbutton",
            background=[("selected", c["accent"]), ("active", c["border"])],
            foreground=[("selected", c["on_accent"]), ("active", c["text"])],
            bordercolor=[("selected", c["accent"])],
            lightcolor=[("selected", c["accent"])],
            darkcolor=[("selected", c["accent"])],
        )

        style.configure(
            "TCheckbutton",
            indicatorbackground=c["surface"],
            indicatorforeground=c["surface"],
            indicatorsize=14,
            indicatormargin=(0, 0, 8, 0),
            upperbordercolor=c["border"],
            lowerbordercolor=c["border"],
            padding=(0, 4),
        )
        style.map(
            "TCheckbutton",
            background=[("active", c["bg"])],
            indicatorbackground=[("selected", c["accent"])],
            indicatorforeground=[("selected", c["accent"])],
            upperbordercolor=[("selected", c["accent"])],
            lowerbordercolor=[("selected", c["accent"])],
        )

        style.configure(
            "Vertical.TScrollbar",
            background=c["border"],
            troughcolor=c["surface"],
            bordercolor=c["surface"],
            lightcolor=c["border"],
            darkcolor=c["border"],
            arrowcolor=c["muted"],
            gripcount=0,
            arrowsize=10,
        )
        style.map("Vertical.TScrollbar", background=[("active", c["muted"])])

    def _text_widget(self, parent: tk.Misc, height: int, font: tuple) -> tk.Text:
        c = COLORS
        return tk.Text(
            parent,
            height=height,
            bg=c["surface"],
            fg=c["text"],
            insertbackground=c["text"],
            selectbackground=c["accent"],
            selectforeground=c["on_accent"],
            relief="flat",
            borderwidth=0,
            highlightthickness=1,
            highlightbackground=c["border"],
            highlightcolor=c["accent"],
            padx=12,
            pady=10,
            wrap="word",
            font=font,
        )

    def _section(self, parent: tk.Misc, text: str) -> ttk.Label:
        return ttk.Label(parent, text=text.upper(), style="Section.TLabel")

    def _build_widgets(self) -> None:
        header = ttk.Frame(self)
        header.pack(fill="x", pady=(0, 20))
        ttk.Label(header, text="yt-dlp audio", style="Title.TLabel").pack(anchor="w")
        ttk.Label(header, text="Pega enlaces de YouTube y extrae el audio.", style="Muted.TLabel").pack(anchor="w")


        self._section(self, "Enlaces · uno por línea").pack(anchor="w", pady=(0, 6))
        self.url_text = self._text_widget(self, height=5, font=(self.ui_font, 10))
        self.url_text.pack(fill="x", pady=(0, 18))

        self._section(self, "Destino").pack(anchor="w", pady=(0, 6))
        out_frame = ttk.Frame(self)
        out_frame.pack(fill="x", pady=(0, 18))
        self.output_var = tk.StringVar(value=DEFAULT_OUTPUT_DIR)
        ttk.Entry(out_frame, textvariable=self.output_var).pack(side="left", fill="x", expand=True)
        ttk.Button(out_frame, text="Elegir…", style="Ghost.TButton", command=self._choose_dir).pack(
            side="left", padx=(8, 0)
        )

        main_opts = ttk.Frame(self)
        main_opts.pack(fill="x", pady=(0, 14))

        fmt_col = ttk.Frame(main_opts)
        fmt_col.pack(side="left", anchor="n")
        self._section(fmt_col, "Formato").pack(anchor="w", pady=(0, 6))
        self.format_var = tk.StringVar(value="wav")
        fmt_row = ttk.Frame(fmt_col)
        fmt_row.pack(anchor="w")
        for fmt in AUDIO_FORMATS:
            ttk.Radiobutton(
                fmt_row, text=fmt.upper(), value=fmt, variable=self.format_var, style="Pill.Toolbutton"
            ).pack(side="left", padx=(0, 4))

        q_col = ttk.Frame(main_opts)
        q_col.pack(side="left", anchor="n", padx=(32, 0))
        self._section(q_col, "Calidad").pack(anchor="w", pady=(0, 6))
        self.quality_var = tk.StringVar(value=QUALITY_OPTIONS[0][1])
        q_row = ttk.Frame(q_col)
        q_row.pack(anchor="w")
        for label, value in QUALITY_OPTIONS:
            ttk.Radiobutton(
                q_row, text=label, value=value, variable=self.quality_var, style="Pill.Toolbutton"
            ).pack(side="left", padx=(0, 4))

        self.adv_toggle = ttk.Button(self, style="Link.TButton", command=self._toggle_advanced, cursor="hand2")
        self.adv_toggle.pack(anchor="w", pady=(4, 10))
        self._build_advanced()
        self._refresh_toggle_text()

        self.action_row = ttk.Frame(self)
        self.action_row.pack(fill="x", pady=(8, 10))
        self.download_btn = ttk.Button(
            self.action_row, text="Descargar", style="Accent.TButton", command=self._start_download, cursor="hand2"
        )
        self.download_btn.pack(side="left")
        self.cancel_btn = ttk.Button(
            self.action_row, text="Cancelar", style="Ghost.TButton", command=self._cancel_download, state="disabled"
        )
        self.cancel_btn.pack(side="left", padx=(8, 0))
        self.status_var = tk.StringVar(value="Listo")
        ttk.Label(self.action_row, textvariable=self.status_var, style="Muted.TLabel").pack(side="right")

        # Plain frames instead of ttk.Progressbar: clam can't draw a thin, flat bar.
        progress_track = tk.Frame(self, height=4, bg=COLORS["surface"])
        progress_track.pack(fill="x", pady=(0, 18))
        self.progress_fill = tk.Frame(progress_track, bg=COLORS["accent"])
        self.progress_fill.place(x=0, y=0, relheight=1, relwidth=0)

        self._section(self, "Registro").pack(anchor="w", pady=(0, 6))
        log_frame = ttk.Frame(self)
        log_frame.pack(fill="both", expand=True)
        self.log_text = self._text_widget(log_frame, height=8, font=(self.mono_font, 9))
        self.log_text.configure(state="disabled", fg=COLORS["muted"])
        scroll = ttk.Scrollbar(log_frame, orient="vertical", command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=scroll.set)
        self.log_text.pack(side="left", fill="both", expand=True)
        scroll.pack(side="left", fill="y")

    def _build_advanced(self) -> None:
        self.adv_frame = ttk.Frame(self)

        self.playlist_var = tk.BooleanVar(value=False)
        self.thumbnail_var = tk.BooleanVar(value=False)
        self.keepvideo_var = tk.BooleanVar(value=False)
        self.metadata_var = tk.BooleanVar(value=True)
        checks = [
            ("Descargar playlist completa", self.playlist_var),
            ("Incrustar miniatura", self.thumbnail_var),
            ("Conservar vídeo original", self.keepvideo_var),
            ("Añadir metadatos", self.metadata_var),
        ]
        for i, (text, var) in enumerate(checks):
            ttk.Checkbutton(self.adv_frame, text=text, variable=var).grid(
                row=i // 2, column=i % 2, sticky="w", padx=(0, 32)
            )

        self._section(self.adv_frame, "Plantilla de nombre").grid(
            row=2, column=0, columnspan=2, sticky="w", pady=(12, 6)
        )
        self.template_var = tk.StringVar(value="%(title)s.%(ext)s")
        ttk.Entry(self.adv_frame, textvariable=self.template_var).grid(row=3, column=0, columnspan=2, sticky="we")
        self.adv_frame.columnconfigure(1, weight=1)

    def _refresh_toggle_text(self) -> None:
        arrow = "▾" if self._advanced_open else "▸"
        self.adv_toggle.configure(text=f"{arrow}  Opciones avanzadas")

    def _toggle_advanced(self) -> None:
        self._advanced_open = not self._advanced_open
        if self._advanced_open:
            self.adv_frame.pack(fill="x", pady=(0, 12), after=self.adv_toggle)
            self.master.update_idletasks()
            needed = self.master.winfo_reqheight()
            if needed > self.master.winfo_height():
                self.master.geometry(f"{self.master.winfo_width()}x{needed}")
        else:
            self.adv_frame.pack_forget()
        self._refresh_toggle_text()

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
                self.master.after(0, lambda: self._set_progress(pct, f"Descargando… {pct:.0f}%"))
        elif status == "finished":
            self.master.after(0, lambda: self._set_progress(100, "Convirtiendo…"))

    def _set_progress(self, value: float, status: str) -> None:
        self.progress_fill.place_configure(relwidth=value / 100)
        self.status_var.set(status)

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
            audio_quality=self.quality_var.get(),
            filename_template=self.template_var.get().strip() or "%(title)s.%(ext)s",
            download_playlist=self.playlist_var.get(),
            embed_thumbnail=self.thumbnail_var.get(),
            add_metadata=self.metadata_var.get(),
            keep_video=self.keepvideo_var.get(),
        )

        self._downloader = Downloader(self._log, self._on_progress)
        self.download_btn.configure(state="disabled")
        self.cancel_btn.configure(state="normal")
        self._set_progress(0, "Iniciando…")

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
            self.status_var.set("Cancelando…")

    def _on_finished(self) -> None:
        self.download_btn.configure(state="normal")
        self.cancel_btn.configure(state="disabled")
        self.status_var.set("Listo")
        self._log("Proceso terminado.")



def main() -> None:
    if sys.platform == "win32":
        try:
            import ctypes

            ctypes.windll.shcore.SetProcessDpiAwareness(1)
        except Exception:
            pass
    root = tk.Tk()
    if sys.platform == "win32" and os.path.exists(ICON_PATH):
        root.iconbitmap(default=ICON_PATH)
    App(root)
    root.mainloop()


if __name__ == "__main__":
    main()
