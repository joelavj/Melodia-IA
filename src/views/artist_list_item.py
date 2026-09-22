import tkinter as tk
from utils.function import load_image
from utils.constante import BASE_DIR
from models.artist_model import Artist
from controllers.library_controller import library_controller
from views.menu_actions import build_song_context_menu


class ArtistListItem(tk.Frame):
    """Ligne de liste pour un artiste : case à cocher, avatar, nom, menu ⋮."""

    def __init__(self, parent, artist: Artist, on_click_callback=None, on_selection_change=None):
        super().__init__(parent, bg="#2d2d2d", height=60, highlightthickness=0)
        self.pack_propagate(False)

        self.id_artist = artist.id
        self.name = artist.name
        self.selected = False
        self.on_click_callback = on_click_callback
        self.on_selection_change = on_selection_change

        self.select_var = tk.BooleanVar(value=False)
        self.checkbox = tk.Checkbutton(
            self, variable=self.select_var, command=self._on_checkbox_toggle,
            bg="#2d2d2d", activebackground="#2d2d2d", bd=0, highlightthickness=0
        )
        self.checkbox.pack(side="left", padx=(10, 0))

        # cover_path = BASE_DIR / "melodia_ia.png"
        # cover_image = load_image(cover_path, 44, 44)
        # self.cover_label = tk.Label(self, image=cover_image, bg="#2d2d2d", cursor="hand2")
        # self.cover_label.image = cover_image
        # self.cover_label.pack(side="left", padx=10, pady=5)
        # self.cover_label.bind("<Button-1>", self._on_click)

        info_frame = tk.Frame(self, bg="#2d2d2d")
        info_frame.pack(side="left", fill="both", expand=True, padx=5)

        self.name_label = tk.Label(
            info_frame, text=self.name, fg="#ffffff", bg="#2d2d2d",
            font=("Arial", 11, "bold"), anchor="w", cursor="hand2"
        )
        self.name_label.pack(fill="x",pady=(20,0))
        self.name_label.bind("<Button-1>", self._on_click)

        menu_image = load_image(BASE_DIR / "menu-dots-vertical.png", 22, 22)
        self.menu_btn = tk.Label(self, image=menu_image, bg="#2d2d2d", cursor="hand2")
        self.menu_btn.image = menu_image
        self.menu_btn.pack(side="right", padx=10)
        self.menu_btn.bind("<Button-1>", self.show_options_menu)

        # self._widgets_for_bg = [self, self.checkbox, self.cover_label, info_frame,
        #                          self.name_label, self.menu_btn]
        self._widgets_for_bg = [self, self.checkbox, info_frame,
                                 self.name_label, self.menu_btn]

    def _on_click(self, event=None):
        if self.on_click_callback:
            self.on_click_callback(self.id_artist)

    def _on_checkbox_toggle(self):
        self.selected = self.select_var.get()
        self._apply_style()
        if self.on_selection_change:
            self.on_selection_change(self.id_artist, self.selected, self)

    def set_selected(self, value: bool):
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

    def show_options_menu(self, event):
        song_ids = [s.id for s in library_controller.list_songs_artist(self.id_artist)]
        menu = build_song_context_menu(
            self, song_ids,
            on_after_action=None,
            play_label="Lire tous les morceaux",
            on_details=lambda: self._on_click(),
        )
        menu.tk_popup(event.x_root, event.y_root)
