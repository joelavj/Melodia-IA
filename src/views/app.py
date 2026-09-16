from __future__ import annotations

from pathlib import Path
from typing import Any

import customtkinter as ctk
from tkinter import filedialog, messagebox


ACCENT = "#1DB954"
BACKGROUND = "#121212"
SURFACE = "#1E1E1E"
MUTED = "#A0A0A0"


def value_of(item: Any, *names: str, default: str = "") -> str:
    for name in names:
        value = item.get(name) if isinstance(item, dict) else getattr(item, name, None)
        if value is not None and str(value).strip():
            return str(value)
    return default


class MelodiaApp(ctk.CTk):
    """Fenêtre principale, volontairement mince: les contrôleurs portent le métier."""

    tabs = ("Accueil", "Morceaux", "Albums", "Artistes", "Playlists", "Favoris", "File d'attente", "Dossiers")

    def __init__(self) -> None:
        super().__init__()
        self.title("Melod'IA")
        self.geometry("1280x780")
        self.minsize(960, 620)
        self.configure(fg_color=BACKGROUND)
        self.selected_tab = "Accueil"
        self.search_text = ""
        self.status_text = ctk.StringVar(value="Prêt")

        self._build_header()
        self._build_body()
        self._build_player()
        self.refresh()
        self.after(500, self._poll_player)

    def _build_header(self) -> None:
        header = ctk.CTkFrame(self, height=64, fg_color=BACKGROUND, corner_radius=0)
        header.pack(fill="x")
        header.pack_propagate(False)

        ctk.CTkLabel(header, text="Melod'IA", text_color=ACCENT,
                     font=ctk.CTkFont(size=22, weight="bold")).pack(side="left", padx=20)

        self.search = ctk.CTkEntry(
            header, width=360, height=34,
            placeholder_text="Rechercher un titre, un artiste ou un album",
        )
        self.search.pack(side="right", padx=(8, 20))
        self.search.bind("<Return>", lambda _event: self._search())
        ctk.CTkButton(header, text="Rechercher", width=105, command=self._search).pack(side="right")

    def _build_body(self) -> None:
        body = ctk.CTkFrame(self, fg_color=BACKGROUND, corner_radius=0)
        body.pack(fill="both", expand=True)

        self.sidebar = ctk.CTkScrollableFrame(body, width=190, fg_color="#0D0D0D", corner_radius=0)
        self.sidebar.pack(side="left", fill="y")
        for tab in self.tabs:
            ctk.CTkButton(
                self.sidebar, text=tab, anchor="w", height=38,
                fg_color="transparent", hover_color="#292929",
                command=lambda name=tab: self.show_tab(name),
            ).pack(fill="x", padx=8, pady=2)
        ctk.CTkButton(
            self.sidebar, text="Importer un dossier", anchor="w", height=38,
            fg_color=ACCENT, text_color="#000000", hover_color="#17A34A",
            command=self.import_directory,
        ).pack(fill="x", padx=8, pady=(18, 2))

        self.content = ctk.CTkFrame(body, fg_color=BACKGROUND, corner_radius=0)
        self.content.pack(side="left", fill="both", expand=True, padx=18, pady=14)

    def _build_player(self) -> None:
        player = ctk.CTkFrame(self, height=110, fg_color=SURFACE, corner_radius=0)
        player.pack(fill="x")
        player.pack_propagate(False)

        info = ctk.CTkFrame(player, fg_color="transparent")
        info.pack(side="left", padx=18, fill="y")
        self.song_label = ctk.CTkLabel(info, text="Aucun morceau", anchor="w",
                                       font=ctk.CTkFont(size=14, weight="bold"))
        self.song_label.pack(anchor="w")
        self.artist_label = ctk.CTkLabel(info, text="", text_color=MUTED, anchor="w")
        self.artist_label.pack(anchor="w")
        self.lyrics_label = ctk.CTkLabel(info, text="Paroles non disponibles", text_color="#D9D9D9",
                                        anchor="w", wraplength=420, justify="left")
        self.lyrics_label.pack(anchor="w", pady=(4, 0))

        controls = ctk.CTkFrame(player, fg_color="transparent")
        controls.pack(expand=True)
        ctk.CTkButton(controls, text="<<", width=42, command=self.previous).pack(side="left", padx=4)
        self.play_button = ctk.CTkButton(controls, text="Play", width=72, fg_color=ACCENT,
                                         text_color="#000000", hover_color="#17A34A",
                                         command=self.play_pause)
        self.play_button.pack(side="left", padx=4)
        ctk.CTkButton(controls, text=">>", width=42, command=self.next_song).pack(side="left", padx=4)

        self.volume = ctk.CTkSlider(player, from_=0, to=100, width=130, command=self.change_volume)
        self.volume.set(70)
        self.volume.pack(side="right", padx=(8, 18))
        ctk.CTkLabel(player, textvariable=self.status_text, text_color=MUTED).pack(side="right")

    def _controllers(self):
        from controllers.directory_controller import directory_controller
        from controllers.favori_controller import favori_controller
        from controllers.library_controller import library_controller
        from controllers.player_controller import player_controller
        from controllers.playlist_controller import PlaylistController
        from controllers.queue_controller import queue_controller

        return (directory_controller, favori_controller, library_controller,
                player_controller, PlaylistController(), queue_controller)

    def refresh(self) -> None:
        self._clear_content()
        try:
            self._render_tab(self.selected_tab)
        except Exception as error:
            self.status_text.set(f"Bibliothèque indisponible: {error}")
            ctk.CTkLabel(self.content, text="Impossible de charger la bibliothèque.",
                         text_color="#F08080", font=ctk.CTkFont(size=16)).pack(pady=30)

    def _clear_content(self) -> None:
        for widget in self.content.winfo_children():
            widget.destroy()

    def show_tab(self, tab: str) -> None:
        self.selected_tab = tab
        self.refresh()

    def _render_tab(self, tab: str) -> None:
        _, _, library, _, _, _ = self._controllers()
        ctk.CTkLabel(self.content, text=tab, font=ctk.CTkFont(size=24, weight="bold")).pack(anchor="w", pady=(0, 14))

        if tab == "Accueil":
            items = library.list_songs()[:8]
            self._render_song_list(items, "Écoutes récentes")
        elif tab == "Morceaux":
            self._render_song_list(library.list_songs())
        elif tab == "Favoris":
            self._render_song_list(library.list_favorite())
        elif tab == "File d'attente":
            self._render_song_list(library.list_queue(), queue=True)
        elif tab == "Albums":
            self._render_generic(library.list_albums(), "title", "artists")
        elif tab == "Artistes":
            self._render_generic(library.list_artists(), "name")
        elif tab == "Dossiers":
            self._render_generic(library.list_directories(), "path")
        elif tab == "Playlists":
            self._render_playlists(library.list_playlists())

    def _render_song_list(self, songs: list, title: str | None = None, queue: bool = False) -> None:
        if title:
            ctk.CTkLabel(self.content, text=title, text_color=MUTED).pack(anchor="w", pady=(0, 8))
        visible = [song for song in songs if self._matches(song)]
        if not visible:
            ctk.CTkLabel(self.content, text="Aucun morceau à afficher.", text_color=MUTED).pack(pady=30)
            return
        scroll = ctk.CTkScrollableFrame(self.content, fg_color="transparent")
        scroll.pack(fill="both", expand=True)
        for song in visible:
            row = ctk.CTkFrame(scroll, fg_color=SURFACE, height=52)
            row.pack(fill="x", pady=3)
            row.pack_propagate(False)
            title_text = value_of(song, "title", default="Titre inconnu")
            artist_text = value_of(song, "artists", default="Artiste inconnu")
            ctk.CTkLabel(row, text=title_text, anchor="w", width=260).pack(side="left", padx=12)
            ctk.CTkLabel(row, text=artist_text, text_color=MUTED, anchor="w").pack(side="left", fill="x", expand=True)
            ctk.CTkButton(row, text="Play", width=58, command=lambda item=song: self.play_song(item)).pack(side="right", padx=5)
            if queue:
                ctk.CTkButton(row, text="Retirer", width=70, command=lambda item=song: self.remove_from_queue(item)).pack(side="right", padx=5)
            else:
                ctk.CTkButton(row, text="+ File", width=58, command=lambda item=song: self.add_to_queue(item)).pack(side="right", padx=5)

    def _render_generic(self, items: list, primary: str, secondary: str | None = None) -> None:
        scroll = ctk.CTkScrollableFrame(self.content, fg_color="transparent")
        scroll.pack(fill="both", expand=True)
        for item in items:
            title = value_of(item, primary, default="Sans nom")
            subtitle = value_of(item, secondary, default="") if secondary else ""
            ctk.CTkLabel(scroll, text=f"{title}  {subtitle}", anchor="w",
                         fg_color=SURFACE, corner_radius=6, height=46).pack(fill="x", pady=3, padx=3)
        if not items:
            ctk.CTkLabel(scroll, text="Aucun élément à afficher.", text_color=MUTED).pack(pady=30)

    def _render_playlists(self, playlists: list) -> None:
        toolbar = ctk.CTkFrame(self.content, fg_color="transparent")
        toolbar.pack(fill="x", pady=(0, 10))
        ctk.CTkButton(toolbar, text="Nouvelle playlist", fg_color=ACCENT, text_color="#000000",
                      command=self.create_playlist).pack(side="left")
        scroll = ctk.CTkScrollableFrame(self.content, fg_color="transparent")
        scroll.pack(fill="both", expand=True)
        _, _, library, _, _, _ = self._controllers()
        for playlist in playlists:
            row = ctk.CTkFrame(scroll, fg_color=SURFACE, height=52)
            row.pack(fill="x", pady=3)
            row.pack_propagate(False)
            name = value_of(playlist, "name", default="Playlist")
            songs = library.list_songs_playlist(int(value_of(playlist, "id", default="0")))
            ctk.CTkLabel(row, text=name, anchor="w").pack(side="left", padx=12)
            ctk.CTkLabel(row, text=f"{len(songs)} morceau(x)", text_color=MUTED).pack(side="left")
            ctk.CTkButton(row, text="Play", width=58, command=lambda p=playlist: self.play_playlist(p)).pack(side="right", padx=8)
        if not playlists:
            ctk.CTkLabel(scroll, text="Aucune playlist.", text_color=MUTED).pack(pady=30)

    def _matches(self, item: Any) -> bool:
        query = self.search_text.lower()
        return not query or query in " ".join((value_of(item, "title"), value_of(item, "artists"), value_of(item, "album"))).lower()

    def _search(self) -> None:
        self.search_text = self.search.get().strip()
        self.refresh()

    def import_directory(self) -> None:
        path = filedialog.askdirectory(title="Sélectionner un dossier musical")
        if not path:
            return
        try:
            directory, _, _, _, _, _ = self._controllers()
            directory.add(path)
            self.status_text.set(f"Dossier importé: {Path(path).name}")
            self.refresh()
        except Exception as error:
            messagebox.showerror("Import impossible", str(error))

    def play_song(self, song: Any) -> None:
        try:
            _, _, _, player, _, _ = self._controllers()
            player.play_song(int(value_of(song, "id", default="0")))
            self.update_player()
        except Exception as error:
            self.status_text.set(f"Lecture impossible: {error}")

    def play_playlist(self, playlist: Any) -> None:
        try:
            _, _, library, _, playlists, _ = self._controllers()
            playlist_id = int(value_of(playlist, "id", default="0"))
            songs = library.list_songs_playlist(playlist_id)
            if songs:
                playlists.play(playlist_id, int(value_of(songs[0], "id", default="0")))
                self.update_player()
        except Exception as error:
            self.status_text.set(f"Playlist indisponible: {error}")

    def create_playlist(self) -> None:
        name = ctk.CTkInputDialog(text="Nom de la playlist", title="Nouvelle playlist").get_input()
        if name and name.strip():
            try:
                self._controllers()[4].create(name.strip())
                self.refresh()
            except Exception as error:
                messagebox.showerror("Création impossible", str(error))

    def add_to_queue(self, song: Any) -> None:
        self._controllers()[5].add_song(int(value_of(song, "id", default="0")))
        self.refresh()

    def remove_from_queue(self, song: Any) -> None:
        self._controllers()[5].remove_song(int(value_of(song, "id", default="0")))
        self.refresh()

    def play_pause(self) -> None:
        self._controllers()[3].play_song()
        self.update_player()

    def next_song(self) -> None:
        self._controllers()[3].next_song()
        self.update_player()

    def previous(self) -> None:
        self._controllers()[3].previous_song()
        self.update_player()

    def change_volume(self, value: float) -> None:
        self._controllers()[3].change_volume(int(value))

    def update_player(self) -> None:
        try:
            status = self._controllers()[3].player_status()
            song = status["song"]
            if song is None:
                self.song_label.configure(text="Aucun morceau")
                self.artist_label.configure(text="")
                self.lyrics_label.configure(text="Paroles non disponibles")
            else:
                self.song_label.configure(text=value_of(song, "title", default="Titre inconnu"))
                self.artist_label.configure(text=value_of(song, "artists", default="Artiste inconnu"))
                lyric = self._controllers()[3].current_lyric(id_song=int(value_of(song, "id", default="0")))
                self.lyrics_label.configure(text=lyric or "Paroles non disponibles")
            self.play_button.configure(text="Pause" if status["is_playing"] else "Play")
        except Exception as error:
            self.status_text.set(f"Lecteur indisponible: {error}")

    def _poll_player(self) -> None:
        self.update_player()
        self.after(500, self._poll_player)


def run() -> None:
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("green")
    app = MelodiaApp()
    app.mainloop()