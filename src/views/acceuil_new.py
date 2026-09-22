import customtkinter as ctk
from controllers.library_controller import library_controller
from controllers.player_controller import player_controller
from views.album_card import AlbumCard
from views.artist_list_item import ArtistListItem
from views.song_list_item import SongListItem
from views.album_details_view import AlbumDetailsView
from views.artist_details_view import ArtistDetailsView
from views.selection_action_bar import SelectionActionBar


class Acceuil(ctk.CTkFrame):
    """Section Accueil : onglets Album / Artiste / Morceau, sélection multiple,
    ouverture d'un album/artiste dans une vue détail avec conservation du scroll."""

    GRID_COLUMNS = 4

    def __init__(self, master):
        super().__init__(master, fg_color="#1e1e1e")

        self.current_tab = "Album"
        self.selected_items = {}          # widget -> id (dans l'onglet courant)
        self.scroll_positions = {"Album": 0.0, "Artiste": 0.0, "Morceau": 0.0}
        self.detail_scroll_positions = {}  # clé ("album", id) / ("artiste", id) -> fraction
        self.albums_by_id = {}
        self.artists_by_id = {}
        self.detail_view = None
        self.detail_key = None

        # ===== VUE "NAVIGATION" (onglets + recherche + contenu) =====
        self.browse_frame = ctk.CTkFrame(self, fg_color="#1e1e1e")
        self.browse_frame.pack(fill="both", expand=True)
        self.browse_frame.grid_rowconfigure(2, weight=1)
        self.browse_frame.grid_columnconfigure(0, weight=1)

        # --- Barre du haut : onglets + recherche ---
        top_bar = ctk.CTkFrame(self.browse_frame, fg_color="#2c3e50", height=60)
        top_bar.grid(row=0, column=0, sticky="ew")
        top_bar.grid_propagate(False)
        top_bar.grid_columnconfigure(1, weight=1)

        tabs_frame = ctk.CTkFrame(top_bar, fg_color="#2c3e50")
        tabs_frame.grid(row=0, column=0, sticky="w", padx=10, pady=10)

        self.boutons = {}
        for i, nom in enumerate(["Album", "Artiste", "Morceau"]):
            btn = ctk.CTkButton(
                tabs_frame, text=nom, command=lambda n=nom: self.changer_onglet(n),
                fg_color="#1abc9c" if nom == "Album" else "#34495e",
                text_color="white", width=100, height=35, font=("Arial", 12)
            )
            btn.grid(row=0, column=i, padx=5)
            self.boutons[nom] = btn

        search_frame = ctk.CTkFrame(top_bar, fg_color="#2c3e50")
        search_frame.grid(row=0, column=2, sticky="e", padx=10, pady=10)
        self.search_var = ctk.StringVar()
        self.search_var.trace("w", lambda *_: self.search_content())
        ctk.CTkEntry(
            search_frame, textvariable=self.search_var, placeholder_text="Rechercher...",
            width=250, height=35, font=("Arial", 11)
        ).pack(side="left", padx=5)

        # --- Barre d'action (sélection) ---
        self.action_bar = SelectionActionBar(
            self.browse_frame, get_song_ids=self._resolve_selected_song_ids,
            on_after_action=self.clear_selection, on_cancel=self.clear_selection
        )
        # non affichée initialement (pas de sélection)

        # --- Zone de contenu défilante ---
        self.scrollable_frame = ctk.CTkScrollableFrame(self.browse_frame, fg_color="#1e1e1e", label_text="")
        self.scrollable_frame.grid(row=2, column=0, sticky="nsew")
        for c in range(self.GRID_COLUMNS):
            self.scrollable_frame.grid_columnconfigure(c, weight=1)
        self.frame_content = self.scrollable_frame

        self.afficher_albums()

    # ------------------------------------------------------------------
    # Navigation entre onglets
    # ------------------------------------------------------------------
    def changer_onglet(self, nom_onglet: str):
        self.search_var.set("")
        self.clear_selection()

        for nom, btn in self.boutons.items():
            btn.configure(fg_color="#1abc9c" if nom == nom_onglet else "#34495e")

        self.current_tab = nom_onglet
        self._clear_content()

        if nom_onglet == "Album":
            self.afficher_albums()
        elif nom_onglet == "Artiste":
            self.afficher_artistes()
        elif nom_onglet == "Morceau":
            self.afficher_morceaux()

    def _clear_content(self):
        for child in self.frame_content.winfo_children():
            child.destroy()

    def _empty_message(self, text: str):
        ctk.CTkLabel(self.frame_content, text=text, text_color="gray", font=("Arial", 12)).pack(pady=50)

    # ------------------------------------------------------------------
    # Affichage des trois types de contenu
    # ------------------------------------------------------------------
    def afficher_albums(self, albums=None):
        try:
            albums = albums if albums is not None else library_controller.list_albums()
            self.albums_by_id = {a.id: a for a in albums}
            if not albums:
                self._empty_message("Aucun album disponible. Ajoutez un répertoire dans les paramètres.")
                return
            for i, album in enumerate(albums):
                self.frame_content.columnconfigure(i % self.GRID_COLUMNS, weight=0)
                self.frame_content.rowconfigure(i // self.GRID_COLUMNS, weight=0)
                card = AlbumCard(
                    self.frame_content, album,
                    on_click_callback=self.open_album,
                    on_selection_change=self._handle_selection_change,
                )
                card.grid(row=i // self.GRID_COLUMNS, column=i % self.GRID_COLUMNS, padx=8, pady=8)
        except Exception as e:
            self._empty_message(f"Erreur : {e}")

    def afficher_artistes(self, artists=None):
        try:
            artists = artists if artists is not None else library_controller.list_artists()
            self.artists_by_id = {a.id: a for a in artists}
            if not artists:
                self._empty_message("Aucun artiste disponible.")
                return
            for artist in artists:
                item = ArtistListItem(
                    self.frame_content, artist,
                    on_click_callback=self.open_artist,
                    on_selection_change=self._handle_selection_change,
                )
                item.pack(fill="x", padx=10, pady=3)
        except Exception as e:
            self._empty_message(f"Erreur : {e}")

    def afficher_morceaux(self, songs=None):
        try:
            songs = songs if songs is not None else library_controller.list_songs()
            if not songs:
                self._empty_message("Aucun morceau disponible.")
                return
            for song in songs:
                item = SongListItem(
                    self.frame_content, song,
                    on_play_callback=self.play_song,
                    on_selection_change=self._handle_selection_change,
                )
                item.pack(fill="x", padx=10, pady=3)
        except Exception as e:
            self._empty_message(f"Erreur : {e}")

    # ------------------------------------------------------------------
    # Recherche (limitée à l'onglet courant)
    # ------------------------------------------------------------------
    def search_content(self):
        term = self.search_var.get().strip().lower()
        self.clear_selection()
        self._clear_content()

        if not term:
            {"Album": self.afficher_albums, "Artiste": self.afficher_artistes,
             "Morceau": self.afficher_morceaux}[self.current_tab]()
            return

        try:
            if self.current_tab == "Album":
                albums = [a for a in library_controller.list_albums() if term in a.title.lower()]
                self.afficher_albums(albums)
            elif self.current_tab == "Artiste":
                artists = [a for a in library_controller.list_artists() if term in a.name.lower()]
                self.afficher_artistes(artists)
            elif self.current_tab == "Morceau":
                songs = [s for s in library_controller.list_songs() if term in s.title.lower()]
                self.afficher_morceaux(songs)
        except Exception as e:
            self._empty_message(f"Erreur : {e}")

    # ------------------------------------------------------------------
    # Sélection multiple (albums, artistes ou morceaux selon l'onglet)
    # ------------------------------------------------------------------
    def _handle_selection_change(self, item_id, selected, widget):
        if selected:
            self.selected_items[widget] = item_id
        else:
            self.selected_items.pop(widget, None)
        self._update_action_bar()

    def _update_action_bar(self):
        if self.selected_items:
            self.action_bar.update_count(len(self.selected_items))
            self.action_bar.grid(row=1, column=0, sticky="ew")
        else:
            self.action_bar.grid_forget()

    def clear_selection(self):
        for widget in list(self.selected_items.keys()):
            widget.set_selected(False)
        self.selected_items.clear()
        self.action_bar.grid_forget()

    def _resolve_selected_song_ids(self) -> list[int]:
        """Traduit la sélection courante (albums/artistes/morceaux) en une
        liste d'identifiants de morceaux, seule unité que le backend manipule."""
        ids = list(self.selected_items.values())
        if self.current_tab == "Album":
            song_ids = []
            for album_id in ids:
                song_ids.extend(s.id for s in library_controller.list_songs_album(album_id))
            return song_ids
        if self.current_tab == "Artiste":
            song_ids = []
            for artist_id in ids:
                song_ids.extend(s.id for s in library_controller.list_songs_artist(artist_id))
            return song_ids
        return ids  # Morceau : ce sont déjà des id_song

    # ------------------------------------------------------------------
    # Lecture directe d'un morceau (onglet Morceau)
    # ------------------------------------------------------------------
    def play_song(self, id_song: int):
        player_controller.play_song(id_song)

    # ------------------------------------------------------------------
    # Ouverture des vues détail (album / artiste) avec mémoire du scroll
    # ------------------------------------------------------------------
    def _save_browse_scroll(self):
        try:
            self.scroll_positions[self.current_tab] = self.scrollable_frame._parent_canvas.yview()[0]
        except Exception:
            pass

    def _restore_browse_scroll(self):
        try:
            self.scrollable_frame._parent_canvas.yview_moveto(self.scroll_positions.get(self.current_tab, 0.0))
        except Exception:
            pass

    def open_album(self, album_id: int):
        album = self.albums_by_id.get(album_id)
        if album is None:
            return
        self._save_browse_scroll()
        self.clear_selection()
        self.browse_frame.pack_forget()

        self.detail_key = ("album", album_id)
        self.detail_view = AlbumDetailsView(
            self, album, on_back_callback=self._close_detail,
            initial_scroll=self.detail_scroll_positions.get(self.detail_key, 0.0)
        )
        self.detail_view.pack(fill="both", expand=True)

    def open_artist(self, artist_id: int):
        artist = self.artists_by_id.get(artist_id)
        if artist is None:
            return
        self._save_browse_scroll()
        self.clear_selection()
        self.browse_frame.pack_forget()

        self.detail_key = ("artiste", artist_id)
        self.detail_view = ArtistDetailsView(
            self, artist, on_back_callback=self._close_detail,
            initial_scroll=self.detail_scroll_positions.get(self.detail_key, 0.0)
        )
        self.detail_view.pack(fill="both", expand=True)

    def _close_detail(self, scroll_fraction: float):
        if self.detail_key is not None:
            self.detail_scroll_positions[self.detail_key] = scroll_fraction
        if self.detail_view is not None:
            self.detail_view.destroy()
        self.detail_view = None
        self.detail_key = None

        self.browse_frame.pack(fill="both", expand=True)
        self.after(50, self._restore_browse_scroll)
