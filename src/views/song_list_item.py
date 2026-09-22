import tkinter as tk
from utils.function import load_image
from utils.constante import BASE_DIR
from controllers.favori_controller import favori_controller
from controllers.library_controller import library_controller
from views.menu_actions import build_song_context_menu


class SongListItem(tk.Frame):
    """Ligne de liste pour un morceau : titre - artiste / album, durée, menu ⋮."""

    def __init__(self, parent, song, on_click_callback=None, on_play_callback=None,
                 on_selection_change=None, show_selection=True):
        super().__init__(parent, bg="#2d2d2d", height=56, highlightthickness=0)
        self.pack_propagate(False)

        self.id_song = song.id
        self.title = song.title
        self.artists = ", ".join(song.artists) if isinstance(song.artists, list) else song.artists
        self.album = song.album
        self.duration = song.duration
        self.favori = bool(getattr(song, "favori", False))
        self.selected = False
        self.on_click_callback = on_click_callback
        self.on_play_callback = on_play_callback
        self.on_selection_change = on_selection_change

        if show_selection:
            self.select_var = tk.BooleanVar(value=False)
            self.checkbox = tk.Checkbutton(
                self, variable=self.select_var, command=self._on_checkbox_toggle,
                bg="#2d2d2d", activebackground="#2d2d2d", bd=0, highlightthickness=0
            )
            self.checkbox.pack(side="left", padx=(10, 0))
        else:
            self.checkbox = None

        # cover_path = getattr(song, "cover_path", None) or BASE_DIR / "melodia_ia.png"
        # cover_image = load_image(cover_path, 44, 44)
        # self.cover_label = tk.Label(self, image=cover_image, bg="#2d2d2d", cursor="hand2")
        # self.cover_label.image = cover_image
        # self.cover_label.pack(side="left", padx=10, pady=5)
        # self.cover_label.bind("<Button-1>", self._on_click)

        info_frame = tk.Frame(self, bg="#2d2d2d")
        info_frame.pack(side="left", fill="both", expand=True, padx=5)

        self.title_label = tk.Label(
            info_frame, text=f"{self.title} - {self.artists} / {self.album}",
            fg="#ffffff", bg="#2d2d2d", font=("Arial", 10, "bold"), anchor="w", cursor="hand2"
        )
        self.title_label.pack(fill="x",pady=(20,0))
        self.title_label.bind("<Button-1>", self._on_click)

        actions_frame = tk.Frame(self, bg="#2d2d2d")
        actions_frame.pack(side="right", padx=10)

        minutes, seconds = divmod(self.duration, 60)
        self.duration_label = tk.Label(
            actions_frame, text=f"{minutes}:{seconds:02d}", fg="#999999",
            bg="#2d2d2d", font=("Arial", 9)
        )
        self.duration_label.pack(side="left", padx=5)

        menu_image = load_image(BASE_DIR / "menu-dots-vertical.png", 22, 22)
        self.menu_btn = tk.Label(actions_frame, image=menu_image, bg="#2d2d2d", cursor="hand2")
        self.menu_btn.image = menu_image
        self.menu_btn.pack(side="left", padx=5)
        self.menu_btn.bind("<Button-1>", self.show_options_menu)

        self._widgets_for_bg = [self, info_frame, self.title_label,
                                 actions_frame, self.duration_label, self.menu_btn]
        if self.checkbox is not None:
            self._widgets_for_bg.append(self.checkbox)

    def _on_click(self, event=None):
        if self.on_play_callback:
            self.on_play_callback(self.id_song)

    def _on_checkbox_toggle(self):
        self.selected = self.select_var.get()
        self._apply_style()
        if self.on_selection_change:
            self.on_selection_change(self.id_song, self.selected, self)

    def set_selected(self, value: bool):
        if self.checkbox is None:
            return
        self.selected = value
        self.select_var.set(value)
        self._apply_style()

    def _apply_style(self):
        bg = "#3d3d3d" if self.selected else "#2d2d2d"
        for w in self._widgets_for_bg:
            try:
                w.configure(bg=bg)
            except tk.TclError:
                pass

    def _toggle_favori(self):
        if self.favori:
            favori_controller.remove_favori(self.id_song)
        else:
            favori_controller.add_favori(self.id_song)
        self.favori = not self.favori

    def _show_details(self):
        info = library_controller.info_song(self.id_song) or None
        dialog = tk.Toplevel(self)
        dialog.title("Détails du morceau")
        dialog.configure(bg="#2d2d2d")
        dialog.resizable(False, False)
        rows = [
            ("Titre", self.title),
            ("Artiste(s)", ", ".join(info.artists) if info and isinstance(info.artists, list) else self.artists),
            ("Album", self.album),
            ("Genre", getattr(info, "genre", "") if info else ""),
            ("Durée", f"{self.duration // 60}:{self.duration % 60:02d}"),
        ]
        for label, value in rows:
            row = tk.Frame(dialog, bg="#2d2d2d")
            row.pack(fill="x", padx=15, pady=4)
            tk.Label(row, text=f"{label} :", fg="#999999", bg="#2d2d2d",
                     font=("Arial", 9, "bold"), width=12, anchor="w").pack(side="left")
            tk.Label(row, text=str(value), fg="white", bg="#2d2d2d",
                     font=("Arial", 9), anchor="w").pack(side="left")
        tk.Button(dialog, text="Fermer", command=dialog.destroy,
                  bg="#4a4a4a", fg="white", relief="flat").pack(pady=(5, 15))

    def show_options_menu(self, event):
        menu = build_song_context_menu(
            self, [self.id_song],
            on_after_action=None,
            favori_state=self.favori,
            on_toggle_favori=self._toggle_favori,
            on_details=self._show_details,
        )
        menu.tk_popup(event.x_root, event.y_root)
