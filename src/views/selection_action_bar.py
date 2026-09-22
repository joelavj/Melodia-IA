import tkinter as tk
from utils.function import load_image
from utils.constante import BASE_DIR
from controllers.queue_controller import queue_controller
from controllers.player_controller import player_controller
from controllers.favori_controller import favori_controller
from controllers.playlist_controller import playlist_controller
from controllers.library_controller import library_controller


class SelectionActionBar(tk.Frame):
    """Barre d'action affichée quand un ou plusieurs éléments sont sélectionnés.

    `get_song_ids` doit être une fonction sans argument qui retourne la liste
    des identifiants de morceaux concernés par la sélection courante (que la
    sélection porte sur des albums, des artistes ou des morceaux, elle est
    toujours résolue en identifiants de morceaux avant d'agir sur le backend).
    `on_after_action` est appelé après chaque action pour vider la sélection.
    """

    def __init__(self, parent, get_song_ids, on_after_action, on_cancel):
        super().__init__(parent, bg="#3d3d3d", height=44)
        self.pack_propagate(False)

        self.get_song_ids = get_song_ids
        self.on_after_action = on_after_action
        self.on_cancel = on_cancel

        self.count_label = tk.Label(
            self, text="", fg="white", bg="#3d3d3d", font=("Arial", 10, "bold")
        )
        self.count_label.pack(side="left", padx=15)

        self._make_button("Lire", self._play).pack(side="left", padx=4)
        self._make_button("Ajouter à la file d'attente", self._add_queue).pack(side="left", padx=4)
        self._make_button("Ajouter aux favoris", self._add_favori).pack(side="left", padx=4)
        self._make_button("Ajouter à une playlist ▾", self._show_playlist_menu).pack(side="left", padx=4)

        cross_image = load_image(BASE_DIR / "cross.png", 16, 16)
        cancel_btn = tk.Label(self, image=cross_image, bg="#3d3d3d", cursor="hand2")
        cancel_btn.image = cross_image
        cancel_btn.pack(side="right", padx=15)
        cancel_btn.bind("<Button-1>", lambda e: self.on_cancel())

    def _make_button(self, text, command):
        return tk.Button(
            self, text=text, command=command,
            bg="#4a4a4a", fg="white", relief="flat",
            activebackground="#5a5a5a", activeforeground="white",
            font=("Arial", 9), padx=8
        )

    def update_count(self, count: int):
        self.count_label.configure(text=f"{count} élément(s) sélectionné(s)")

    def _play(self):
        ids = self.get_song_ids()
        if ids:
            queue_controller.clear_queue()
            for id_song in ids:
                queue_controller.add_song(id_song)
            player_controller.play_song(ids[0])
        self.on_after_action()

    def _add_queue(self):
        for id_song in self.get_song_ids():
            queue_controller.add_song(id_song)
        self.on_after_action()

    def _add_favori(self):
        for id_song in self.get_song_ids():
            favori_controller.add_favori(id_song)
        self.on_after_action()

    def _show_playlist_menu(self):
        ids = self.get_song_ids()
        menu = tk.Menu(self, tearoff=0, bg="#2d2d2d", fg="white", activebackground="#4a4a4a")
        playlists = library_controller.list_playlists()
        if not playlists:
            menu.add_command(label="Aucune playlist", state="disabled")
        for playlist in playlists:
            menu.add_command(
                label=playlist.name,
                command=lambda p=playlist: self._add_to_playlist(p.id, ids)
            )
        menu.tk_popup(self.winfo_pointerx(), self.winfo_pointery())

    def _add_to_playlist(self, id_playlist: int, song_ids: list[int]):
        for id_song in song_ids:
            playlist_controller.add_song(id_playlist, id_song)
        self.on_after_action()
