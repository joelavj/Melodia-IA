import customtkinter as ctk
from controllers.library_controller import library_controller
from controllers.playlist_controller import playlist_controller


class PlaylistDetailWindow(ctk.CTkToplevel):
    """Fenêtre affichant le contenu d'une playlist : lecture, retrait et
    ajout de morceaux. Ouverte depuis PlaylistsView (bouton "Ouvrir").
    """

    def __init__(self, master, playlist, on_change=None):
        super().__init__(master)
        self.playlist = playlist
        self.on_change = on_change

        self.title(playlist.name)
        self.geometry("520x520")
        self.configure(fg_color="#1e1e1e")

        self.grid_rowconfigure(2, weight=1)
        self.grid_columnconfigure(0, weight=1)

        header = ctk.CTkLabel(
            self, text=playlist.name, text_color="white", font=("Arial", 16, "bold")
        )
        header.grid(row=0, column=0, sticky="w", padx=15, pady=(15, 5))

        play_all_btn = ctk.CTkButton(
            self, text="▶ Lire la playlist", command=self.play_all,
            fg_color="#1abc9c", text_color="white"
        )
        play_all_btn.grid(row=0, column=0, sticky="e", padx=15, pady=(15, 5))

        # ===== Ajout d'un morceau =====
        add_frame = ctk.CTkFrame(self, fg_color="#2d2d2d", corner_radius=5)
        add_frame.grid(row=1, column=0, sticky="ew", padx=15, pady=5)
        add_frame.grid_columnconfigure(0, weight=1)

        all_songs = library_controller.list_songs()
        self.songs_by_label = {f"{s.title} - {s.artists}": s.id for s in all_songs}
        values = list(self.songs_by_label.keys()) or ["Aucun morceau disponible"]
        self.selected_song_var = ctk.StringVar(value=values[0])

        song_menu = ctk.CTkOptionMenu(add_frame, variable=self.selected_song_var, values=values)
        song_menu.grid(row=0, column=0, sticky="ew", padx=(10, 5), pady=10)

        add_btn = ctk.CTkButton(
            add_frame, text="+ Ajouter", command=self.add_selected_song,
            fg_color="#3498db", text_color="white", width=90
        )
        add_btn.grid(row=0, column=1, padx=(5, 10), pady=10)

        # ===== Liste des morceaux de la playlist =====
        self.content = ctk.CTkScrollableFrame(self, fg_color="#1e1e1e")
        self.content.grid(row=2, column=0, sticky="nsew", padx=15, pady=(5, 15))
        self.content.grid_columnconfigure(0, weight=1)

        self.refresh()

    def refresh(self):
        for child in self.content.winfo_children():
            child.destroy()

        songs = library_controller.list_song_playlist(self.playlist.id)

        if not songs:
            empty_label = ctk.CTkLabel(self.content, text="Playlist vide", text_color="gray", font=("Arial", 12))
            empty_label.pack(pady=30)
            return

        for song in songs:
            song_frame = ctk.CTkFrame(self.content, fg_color="#2d2d2d", corner_radius=5)
            song_frame.pack(fill="x", padx=5, pady=3)

            song_label = ctk.CTkLabel(
                song_frame, text=f"{song.title} - {song.artists}", text_color="white", font=("Arial", 11)
            )
            song_label.pack(side="left", fill="x", expand=True, padx=10, pady=8)

            play_btn = ctk.CTkButton(
                song_frame, text="▶", command=lambda s=song: self.play_song(s),
                fg_color="#1abc9c", text_color="white", width=35, height=25, font=("Arial", 10)
            )
            play_btn.pack(side="left", padx=5)

            remove_btn = ctk.CTkButton(
                song_frame, text="✕", command=lambda s=song: self.remove_song(s),
                fg_color="#e74c3c", text_color="white", width=35, height=25, font=("Arial", 10)
            )
            remove_btn.pack(side="left", padx=(0, 10))

    def play_all(self):
        playlist_controller.play(self.playlist.id, None)

    def play_song(self, song):
        playlist_controller.play(self.playlist.id, song.id)

    def remove_song(self, song):
        playlist_controller.remove_song(self.playlist.id, song.id)
        self.refresh()
        if self.on_change:
            self.on_change()

    def add_selected_song(self):
        label = self.selected_song_var.get()
        id_song = self.songs_by_label.get(label)
        if id_song is not None:
            playlist_controller.add_song(self.playlist.id, id_song)
            self.refresh()
