import tkinter as tk
from models.artist_model import Artist
from views.song_list_item import SongListItem
from views.selection_action_bar import SelectionActionBar
from controllers.library_controller import library_controller
from controllers.player_controller import player_controller
from utils.function import load_image
from utils.constante import BASE_DIR


class ArtistDetailsView(tk.Frame):
    """Vue détail d'un artiste : nom, liste des morceaux."""

    def __init__(self, master, artist: Artist, on_back_callback=None, initial_scroll: float = 0.0):
        super().__init__(master, bg="#1e1e1e")

        self.artist = artist
        self.on_back_callback = on_back_callback
        self.selected_items = {}

        # ===== BARRE DU HAUT : retour + nom =====
        top_bar = tk.Frame(self, bg="#2c3e50", height=60)
        top_bar.pack(side="top", fill="x")
        top_bar.pack_propagate(False)

        back_image = load_image(BASE_DIR / "en-arriere.png", 22, 22)
        back_btn = tk.Label(top_bar, image=back_image, bg="#2c3e50", cursor="hand2")
        back_btn.image = back_image
        back_btn.pack(side="left", padx=15, pady=10)
        back_btn.bind("<Button-1>", lambda e: self.go_back())

        tk.Label(
            top_bar, text=self.artist.name, fg="white", bg="#2c3e50", font=("Arial", 14, "bold")
        ).pack(side="left", padx=10, pady=10)

        # ===== BARRE D'ACTION (sélection de morceaux) =====
        self.action_bar = SelectionActionBar(
            self, get_song_ids=lambda: list(self.selected_items.values()),
            on_after_action=self.clear_selection, on_cancel=self.clear_selection
        )

        # ===== LISTE DES MORCEAUX (scrollable) =====
        main_frame = tk.Frame(self, bg="#1e1e1e")
        main_frame.pack(side="top", fill="both", expand=True)

        self.canvas = tk.Canvas(main_frame, bg="#1e1e1e", highlightthickness=0)
        self.canvas.pack(side="left", fill="both", expand=True)

        scrollbar = tk.Scrollbar(main_frame, orient="vertical", command=self.canvas.yview)
        scrollbar.pack(side="right", fill="y")
        self.canvas.configure(yscrollcommand=scrollbar.set)

        self.frame_content = tk.Frame(self.canvas, bg="#1e1e1e")
        self.canvas.create_window((0, 0), window=self.frame_content, anchor="nw")
        self.frame_content.bind(
            "<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        songs = library_controller.list_songs_artist(self.artist.id)
        for song in songs:
            item = SongListItem(
                self.frame_content, song=song,
                on_play_callback=self.play_song,
                on_selection_change=self._handle_song_selection,
            )
            item.pack(fill="x", padx=5, pady=2)

        if initial_scroll:
            self.after(50, lambda: self.canvas.yview_moveto(initial_scroll))

    def get_scroll_fraction(self) -> float:
        return self.canvas.yview()[0]

    def _handle_song_selection(self, song_id, selected, widget):
        if selected:
            self.selected_items[widget] = song_id
        else:
            self.selected_items.pop(widget, None)
        self._update_action_bar()

    def _update_action_bar(self):
        if self.selected_items:
            self.action_bar.update_count(len(self.selected_items))
            self.action_bar.pack(side="top", fill="x", after=self.winfo_children()[0])
        else:
            self.action_bar.pack_forget()

    def clear_selection(self):
        for widget in list(self.selected_items.keys()):
            widget.set_selected(False)
        self.selected_items.clear()
        self.action_bar.pack_forget()

    def play_song(self, song_id):
        player_controller.play_song(song_id)

    def go_back(self):
        if self.on_back_callback:
            self.on_back_callback(self.get_scroll_fraction())
