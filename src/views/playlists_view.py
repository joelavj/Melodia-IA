import customtkinter as ctk
from tkinter import messagebox
from controllers.library_controller import library_controller
from controllers.playlist_controller import playlist_controller
from views.playlist_detail_window import PlaylistDetailWindow


class PlaylistsView(ctk.CTkFrame):
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
            text="Playlists",
            text_color="white",
            font=("Arial", 14, "bold")
        )
        title_label.pack(side="left", padx=20, pady=10)

        create_btn = ctk.CTkButton(
            header,
            text="+ Créer",
            command=self.create_playlist,
            fg_color="#1abc9c",
            text_color="white",
            width=100
        )
        create_btn.pack(side="right", padx=20, pady=10)

        # ===== CONTENT =====
        self.content = ctk.CTkScrollableFrame(self, fg_color="#1e1e1e")
        self.content.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
        self.content.grid_columnconfigure(0, weight=1)

        self.refresh()

    def refresh(self):
        """Refresh playlist list. Utilisé aussi par App.changer_page."""
        for child in self.content.winfo_children():
            child.destroy()

        try:
            playlists = library_controller.list_playlists()

            if not playlists:
                empty_label = ctk.CTkLabel(
                    self.content,
                    text="Aucune playlist créée",
                    text_color="gray",
                    font=("Arial", 12)
                )
                empty_label.pack(pady=50)
            else:
                for playlist in playlists:
                    pl_frame = ctk.CTkFrame(self.content, fg_color="#2d2d2d", corner_radius=5)
                    pl_frame.pack(fill="x", padx=5, pady=3)

                    pl_label = ctk.CTkLabel(
                        pl_frame,
                        text=playlist.name,
                        text_color="white",
                        font=("Arial", 11)
                    )
                    pl_label.pack(side="left", fill="x", expand=True, padx=10, pady=8)

                    play_btn = ctk.CTkButton(
                        pl_frame,
                        text="▶",
                        command=lambda p=playlist: self.play_playlist(p),
                        fg_color="#1abc9c",
                        text_color="white",
                        width=35,
                        height=28,
                        font=("Arial", 10)
                    )
                    play_btn.pack(side="left", padx=5)

                    open_btn = ctk.CTkButton(
                        pl_frame,
                        text="Ouvrir",
                        command=lambda p=playlist: self.open_playlist(p),
                        fg_color="#3498db",
                        text_color="white",
                        width=70,
                        height=28,
                        font=("Arial", 9)
                    )
                    open_btn.pack(side="left", padx=5)

                    rename_btn = ctk.CTkButton(
                        pl_frame,
                        text="Renommer",
                        command=lambda p=playlist: self.rename_playlist(p),
                        fg_color="#34495e",
                        text_color="white",
                        width=80,
                        height=28,
                        font=("Arial", 9)
                    )
                    rename_btn.pack(side="left", padx=5)

                    delete_btn = ctk.CTkButton(
                        pl_frame,
                        text="Supprimer",
                        command=lambda p=playlist: self.delete_playlist(p),
                        fg_color="#e74c3c",
                        text_color="white",
                        width=80,
                        height=28,
                        font=("Arial", 9)
                    )
                    delete_btn.pack(side="left", padx=(5, 10))

        except Exception as e:
            error_label = ctk.CTkLabel(
                self.content,
                text=f"Erreur: {str(e)}",
                text_color="red",
                font=("Arial", 11)
            )
            error_label.pack(pady=50)

    def create_playlist(self):
        dialog = ctk.CTkInputDialog(text="Nom de la nouvelle playlist :", title="Créer une playlist")
        name = dialog.get_input()
        if name:
            if playlist_controller.create(name):
                self.refresh()
            else:
                messagebox.showerror("Erreur", f"Une playlist nommée « {name} » existe déjà.")

    def open_playlist(self, playlist):
        PlaylistDetailWindow(self, playlist, on_change=self.refresh)

    def play_playlist(self, playlist):
        playlist_controller.play(playlist.id, None)

    def rename_playlist(self, playlist):
        dialog = ctk.CTkInputDialog(text="Nouveau nom de la playlist :", title="Renommer la playlist")
        name = dialog.get_input()
        if name:
            if playlist_controller.rename(playlist.id, name):
                self.refresh()
            else:
                messagebox.showerror("Erreur", f"Une playlist nommée « {name} » existe déjà.")

    def delete_playlist(self, playlist):
        if messagebox.askyesno("Confirmation", f"Supprimer la playlist « {playlist.name} » ?"):
            playlist_controller.remove(playlist.id)
            self.refresh()
