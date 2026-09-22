import tkinter as tk
from utils.function import load_image
from utils.constante import BASE_DIR
from models.album_model import Album
from controllers.library_controller import library_controller
from views.menu_actions import build_song_context_menu


class AlbumCard(tk.Frame):
    """Carte carrée : pochette en haut, titre/artiste en bas, case à cocher
    de sélection en haut à gauche, menu ⋮ en bas à droite."""

    def __init__(self, parent, album: Album, on_click_callback=None, on_selection_change=None):
        super().__init__(parent, bd=1, relief="solid", bg="#1e1e1e", width=160, height=230,
                          highlightthickness=0)
        self.pack_propagate(False)

        self.id_album = album.id
        self.title = album.title
        self.artists = album.artists
        self.release_year = album.release_year
        self.selected = False
        self.on_click_callback = on_click_callback
        self.on_selection_change = on_selection_change

        # ===== Zone pochette (avec case à cocher en overlay) =====
        cover_zone = tk.Frame(self, bg="#1e1e1e")
        cover_zone.pack(side="top", fill="x", padx=8, pady=(8, 4))

        cover_path = album.cover_path if album.cover_path is not None else BASE_DIR / "melodia_ia.png"
        cover_image = load_image(cover_path, 144, 144)
        self.cover = tk.Label(cover_zone, image=cover_image, bg="#1e1e1e", cursor="hand2")
        self.cover.image = cover_image
        self.cover.place(x=0, y=0)
        cover_zone.configure(width=144, height=144)

        self.select_var = tk.BooleanVar(value=False)
        self.checkbox = tk.Checkbutton(
            cover_zone, variable=self.select_var, command=self._on_checkbox_toggle,
            bg="#1e1e1e", activebackground="#1e1e1e", bd=0, highlightthickness=0
        )
        self.checkbox.place(x=2, y=2)

        self.cover.bind("<Button-1>", lambda e: self.open_content())

        # ===== Zone bas : titre / artiste / menu =====
        self.bottom_frame = tk.Frame(self, bg="#1e1e1e")
        self.bottom_frame.pack(side="bottom", fill="both", expand=True, padx=8, pady=(0, 8))

        self.title_label = tk.Label(
            self.bottom_frame, text=self.title, fg="white", bg="#1e1e1e",
            font=("Arial", 10, "bold"), anchor="nw", justify="left", wraplength=130, cursor="hand2"
        )
        self.title_label.pack(fill="x", anchor="nw")
        self.title_label.bind("<Button-1>", lambda e: self.open_content())

        self.artist_label = tk.Label(
            self.bottom_frame, text=self.artists, fg="#999999", bg="#1e1e1e",
            font=("Arial", 8), anchor="nw", justify="left", wraplength=130, cursor="hand2"
        )
        self.artist_label.pack(fill="x", anchor="nw")
        self.artist_label.bind("<Button-1>", lambda e: self.open_content())

        menu_frame = tk.Frame(self.bottom_frame, bg="#1e1e1e")
        menu_frame.pack(fill="x", pady=(2, 0))

        icone_menu = load_image(BASE_DIR / "menu-dots-vertical.png", 18, 18)
        self.options_btn = tk.Label(menu_frame, image=icone_menu, bg="#1e1e1e", cursor="hand2")
        self.options_btn.image = icone_menu
        self.options_btn.pack(side="right")
        self.options_btn.bind("<Button-1>", self.show_options_menu)

        self._widgets_for_bg = [self, self.bottom_frame, cover_zone, self.cover,
                                 self.checkbox, self.title_label, self.artist_label,
                                 menu_frame, self.options_btn]

    def _on_checkbox_toggle(self):
        self.selected = self.select_var.get()
        self._apply_style()
        if self.on_selection_change:
            self.on_selection_change(self.id_album, self.selected, self)

    def set_selected(self, value: bool):
        """Permet à la vue parente de forcer l'état (ex: désélection groupée)."""
        self.selected = value
        self.select_var.set(value)
        self._apply_style()

    def _apply_style(self):
        bg = "#2d2d2d" if self.selected else "#1e1e1e"
        border = "#1abc9c" if self.selected else "#1e1e1e"
        self.configure(bg=bg, highlightbackground=border, highlightcolor=border,
                        highlightthickness=2 if self.selected else 0)
        for w in self._widgets_for_bg:
            try:
                w.configure(bg=bg)
            except tk.TclError:
                pass

    def open_content(self):
        if self.on_click_callback:
            self.on_click_callback(self.id_album)

    def show_options_menu(self, event):
        song_ids = [s.id for s in library_controller.list_songs_album(self.id_album)]
        menu = build_song_context_menu(
            self, song_ids,
            on_after_action=None,
            play_label="Lire l'album",
            on_details=self.open_content,
        )
        menu.tk_popup(event.x_root, event.y_root)
