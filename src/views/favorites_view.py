import customtkinter as ctk
from controllers.library_controller import library_controller
from controllers.favori_controller import favori_controller


class FavoritesView(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color="#1e1e1e")
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # ===== HEADER =====
        header = ctk.CTkFrame(self, fg_color="#2c3e50", height=60)
        header.grid(row=0, column=0, sticky="ew")
        header.pack_propagate(False)

        title_label = ctk.CTkLabel(
            header,
            text="Favoris",
            text_color="white",
            font=("Arial", 14, "bold")
        )
        title_label.pack(side="left", padx=20, pady=10)

        # ===== CONTENT =====
        self.content = ctk.CTkScrollableFrame(self, fg_color="#1e1e1e")
        self.content.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
        self.content.grid_columnconfigure(0, weight=1)

        self.refresh()

    def refresh(self):
        """Refresh favorites list. Utilisé aussi par App.changer_page."""
        for child in self.content.winfo_children():
            child.destroy()

        try:
            favorites = library_controller.list_favorite()

            if not favorites:
                empty_label = ctk.CTkLabel(
                    self.content,
                    text="Aucun morceau marqué comme favori",
                    text_color="gray",
                    font=("Arial", 12)
                )
                empty_label.pack(pady=50)
            else:
                for song in favorites:
                    song_frame = ctk.CTkFrame(self.content, fg_color="#2d2d2d", corner_radius=5)
                    song_frame.pack(fill="x", padx=5, pady=3)

                    artists = ', '.join(song.artists) if isinstance(song.artists, list) else song.artists
                    song_label = ctk.CTkLabel(
                        song_frame,
                        text=f"{song.title} - {artists}",
                        text_color="white",
                        font=("Arial", 11)
                    )
                    song_label.pack(side="left", fill="x", expand=True, padx=10, pady=8)

                    play_btn = ctk.CTkButton(
                        song_frame,
                        text="▶",
                        command=lambda s=song: self.play_song(s),
                        fg_color="#1abc9c",
                        text_color="white",
                        width=35,
                        height=25,
                        font=("Arial", 10)
                    )
                    play_btn.pack(side="left", padx=5)

                    remove_btn = ctk.CTkButton(
                        song_frame,
                        text="✕",
                        command=lambda s=song: self.remove_favori(s),
                        fg_color="#e74c3c",
                        text_color="white",
                        width=35,
                        height=25,
                        font=("Arial", 10)
                    )
                    remove_btn.pack(side="left", padx=(0, 10))

        except Exception as e:
            error_label = ctk.CTkLabel(
                self.content,
                text=f"Erreur: {str(e)}",
                text_color="red",
                font=("Arial", 11)
            )
            error_label.pack(pady=50)

    def play_song(self, song):
        """Reconstitue la file d'attente à partir des favoris et lance ce morceau."""
        favori_controller.play(song.id)

    def remove_favori(self, song):
        favori_controller.remove_favori(song.id)
        self.refresh()
