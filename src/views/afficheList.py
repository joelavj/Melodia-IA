"""
afficheList.py — CustomTkinter
Affichage dynamique de la bibliothèque (Morceaux, Albums, Artistes, Playlists, File d'attente)
avec gestion de l'ajout et suppression de la file d'attente via QueueController.
"""
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import customtkinter as ctk
from controllers.library_controller import library_controller
from controllers.player_controller import player_controller as pc
from controllers.queue_controller import queue_controller as qc


def _get_val(obj, *keys, default=""):
    """Récupère une valeur sur un objet ou un dictionnaire sans erreur."""
    if obj is None:
        return default
    for key in keys:
        if isinstance(obj, dict):
            val = obj.get(key)
        else:
            val = getattr(obj, key, None)
        if val is not None and str(val).strip() != "":
            return str(val)
    return default


class ListDisplay(ctk.CTkFrame):
    """Zone centrale : onglets Albums / Artistes / Morceaux / Dossiers / Playlists / File d'attente."""

    def __init__(self, master, on_item_click=None, **kwargs):
        super().__init__(master, fg_color="#181818", corner_radius=0, **kwargs)
        self.on_item_click = on_item_click

        self.playlists = {"Favoris": []}

        self.tabview = ctk.CTkTabview(
            self,
            fg_color="#181818",
            segmented_button_fg_color="#242424",
            segmented_button_selected_color="#1DB954",
            segmented_button_selected_hover_color="#17a34a",
        )
        self.tabview.pack(fill="both", expand=True, padx=16, pady=16)

        self.tabs_name = ["Albums", "Artistes", "Morceaux", "Dossiers", "Playlists", "File d'attente"]
        for tab_name in self.tabs_name:
            self.tabview.add(tab_name)

        self.rafraichir()

    def on_import_complete(self, onglet):
        """Déclenché par le Menu lors d'une importation."""
        self.rafraichir()
        self.changer_onglet(onglet)
        self.after(200, self.rafraichir)

    def rafraichir(self):
        """Recharge la bibliothèque et rafraîchit l'affichage des onglets."""
        try:
            library_controller.load()
        except Exception as e:
            print(f"[afficheList] Erreur lors de library_service.load(): {e}")

        morceaux_liste = getattr(library_controller, 'songs', []) 
        dossiers_liste = getattr(library_controller, 'directories', []) 
        queue_liste = getattr(library_controller, 'queue', []) 

        albums_groupes = {}
        artistes_groupes = {}

        for song in morceaux_liste:
            album_nom = _get_val(song, 'album', 'album_title', default='Album inconnu')
            artistes_nom = [_get_val(artist, 'name', default='Artiste inconnu') for artist in song.artists]
            artiste_nom = " , ".join(artistes_nom)

            if album_nom not in albums_groupes:
                albums_groupes[album_nom] = {
                    "titre": album_nom,
                    "artiste": artiste_nom,
                    "morceaux": [song]
                }
            else:
                albums_groupes[album_nom]["morceaux"].append(song)

            if artiste_nom not in artistes_groupes:
                artistes_groupes[artiste_nom] = {
                    "titre": artiste_nom,
                    "count": 1,
                    "object": song
                }
            else:
                artistes_groupes[artiste_nom]["count"] += 1

        # 1. Albums
        liste_albums = [
            {
                "titre": alb["titre"],
                "sous_titre": f"{alb['artiste']} • {len(alb['morceaux'])} titre(s)",
                "object": alb["morceaux"][0]
            }
            for alb in albums_groupes.values()
        ] if albums_groupes else [{"titre": "Aucun album", "sous_titre": "Importez un dossier", "object": None}]

        # 2. Artistes
        liste_artistes = [
            {
                "titre": art["titre"],
                "sous_titre": f"{art['count']} morceau(x)",
                "object": art["object"]
            }
            for art in artistes_groupes.values()
        ] if artistes_groupes else [{"titre": "Aucun artiste", "sous_titre": "Importez un dossier", "object": None}]

        # 3. Afficher TOUS LES MORCEAUX
        liste_morceaux = [
            {
                "titre": _get_val(song, 'title', 'name', 'filename', default=os.path.basename(_get_val(song, 'path')) or 'Titre inconnu'),
                "sous_titre": _get_val(song, 'artist', 'artist_name', default='Artiste inconnu'),
                "object": song
            }
            for song in morceaux_liste
        ] if morceaux_liste else [{"titre": "Aucun morceau", "sous_titre": "Importez des fichiers", "object": None}]

        # 4. Dossiers
        liste_dossiers = []
        for folder in dossiers_liste:
            folder_path = _get_val(folder, 'path')
            folder_id = _get_val(folder, 'id')
            titre = os.path.basename(folder_path) if folder_path else f"Dossier #{folder_id}"
            sous_titre = folder_path if folder_path else f"ID: {folder_id}"
            liste_dossiers.append({"titre": titre, "sous_titre": sous_titre, "object": folder})

        if not liste_dossiers:
            liste_dossiers = [{"titre": "Aucun dossier", "sous_titre": "Importez un répertoire", "object": None}]

        # 5. Playlists
        liste_playlists = [
            {
                "titre": nom_pl,
                "sous_titre": f"{len(chansons)} morceau(x)",
                "object": chansons,
                "nom_playlist": nom_pl
            }
            for nom_pl, chansons in self.playlists.items()
        ]

        data = {
            "Albums": library_controller.albums,
            "Artistes": library_controller.artists,
            "Morceaux": library_controller.songs,
            "Dossiers": library_controller.directories,
            "Playlists": liste_playlists
        }

        for tab_name in self.tabs_name:
            tab = self.tabview.tab(tab_name)
            for widget in tab.winfo_children():
                widget.destroy()

            match (tab_name):
                case "Albums":
                    scroll = ctk.CTkScrollableFrame(tab, fg_color="transparent")
                    scroll.pack(fill="both", expand=True)
                    
                    n_cols = 4
                    for i in range(n_cols):
                        scroll.grid_columnconfigure(i, weight=1)

                        for album in library_controller.albums:
                            card = ctk.CTkFrame(scroll, fg_color="#242424", corner_radius=10, width=170, height=230)
                            card.grid_propagate(False)
                            
                            cover = ctk.CTkFrame(card, fg_color="#1DB954", corner_radius=8, width=150, height=100)
                            cover.pack(padx=10, pady=(10, 6))
                            cover.pack_propagate(False)
                            
                            lbl_titre = ctk.CTkLabel(card, text=album.name, font=ctk.CTkFont(size=13, weight="bold"))
                            lbl_titre.pack(padx=10, anchor="w")
                            
                            lbl_sous = ctk.CTkLabel(card, text="Sous-titre", font=ctk.CTkFont(size=11), text_color="#a0a0a0")
                            lbl_sous.pack(padx=10, anchor="w")
                            
                        for index, item in enumerate(data["Albums"]):
                                row, col = divmod(index, n_cols)
                                self._build_card(scroll, item, tab_name).grid(
                                    row=row, column=col, padx=8, pady=8, sticky="nsew"
                                )
        
        for tab_name in self.tabs_name:
            tab = self.tabview.tab(tab_name)
            for widget in tab.winfo_children():
                widget.destroy()

            if tab_name == "Playlists":
                self._build_playlists_tab(tab, data["Playlists"])
            elif tab_name == "File d'attente":
                self._build_queue_tab(tab, queue_liste)
            else:
                self._build_tab(tab, tab_name, data.get(tab_name, []))

    def changer_onglet(self, nom_onglet):
        if nom_onglet in self.tabs_name:
            self.tabview.set(nom_onglet)

    # --- Onglet Standard ---
    def _build_tab(self, tab, tab_name, items):
        scroll = ctk.CTkScrollableFrame(tab, fg_color="transparent")
        scroll.pack(fill="both", expand=True)

        n_cols = 4
        for i in range(n_cols):
            scroll.grid_columnconfigure(i, weight=1)

        for index, item in enumerate(items):
            row, col = divmod(index, n_cols)
            self._build_card(scroll, item, tab_name).grid(
                row=row, column=col, padx=8, pady=8, sticky="nsew"
            )

    def _build_card(self, parent, item, category):
        card = ctk.CTkFrame(parent, fg_color="#242424", corner_radius=10, width=170, height=230)
        card.grid_propagate(False)

        cover = ctk.CTkFrame(card, fg_color="#1DB954", corner_radius=8, width=150, height=100)
        cover.pack(padx=10, pady=(10, 6))
        cover.pack_propagate(False)

        lbl_titre = ctk.CTkLabel(card, text=item["titre"], font=ctk.CTkFont(size=13, weight="bold"))
        lbl_titre.pack(padx=10, anchor="w")

        lbl_sous = ctk.CTkLabel(card, text=item["sous_titre"], font=ctk.CTkFont(size=11), text_color="#a0a0a0")
        lbl_sous.pack(padx=10, anchor="w")

        # Boutons d'actions pour l'onglet Morceaux
        if category == "Morceaux" and item.get("object") is not None:
            btn_frame = ctk.CTkFrame(card, fg_color="transparent")
            btn_frame.pack(fill="x", padx=6, pady=4, side="bottom")

            btn_playlist = ctk.CTkButton(
                btn_frame, 
                text="+ Playlist", 
                height=22, 
                width=70,
                fg_color="#333333", 
                hover_color="#444444",
                font=ctk.CTkFont(size=10, weight="bold"),
                command=lambda s=item["object"]: self._dialog_ajouter_chanson(s)
            )
            btn_playlist.pack(side="left", padx=2)

            # AJOUTER UN MORCEAU À LA FILE D'ATTENTE
            btn_queue = ctk.CTkButton(
                btn_frame, 
                text="+ File", 
                height=22, 
                width=65,
                fg_color="#1DB954", 
                hover_color="#17a34a",
                text_color="#000000",
                font=ctk.CTkFont(size=10, weight="bold"),
                command=lambda s=item["object"]: self.ajouter_a_la_file(s)
            )
            btn_queue.pack(side="right", padx=2)

        card.bind("<Button-1>", lambda e: self._click(category, item))
        cover.bind("<Button-1>", lambda e: self._click(category, item))
        lbl_titre.bind("<Button-1>", lambda e: self._click(category, item))
        lbl_sous.bind("<Button-1>", lambda e: self._click(category, item))

        return card

    # --- Actions sur la File d'attente ---

    def ajouter_a_la_file(self, song):
        """Ajoute un morceau à la file d'attente via QueueController."""
        song_id = _get_val(song, 'id', 'id_song')
        if song_id:
            try:
                qc.add_song(int(song_id))[cite: 29]
                self.rafraichir()
            except ValueError:
                pass

    def supprimer_de_la_file(self, song):
        """Supprime un morceau de la file d'attente via QueueController."""
        song_id = _get_val(song, 'id', 'id_song')
        if song_id:
            try:
                qc.remove_song(int(song_id))[cite: 29]
                self.rafraichir()
            except ValueError:
                pass

    def _build_queue_tab(self, tab, queue_songs):
        """Affiche les morceaux de la file d'attente."""
        top_bar = ctk.CTkFrame(tab, fg_color="transparent")
        top_bar.pack(fill="x", pady=(0, 10))

        lbl_info = ctk.CTkLabel(
            top_bar, 
            text=f"File d'attente ({len(queue_songs)} morceau(x))", 
            font=ctk.CTkFont(size=16, weight="bold")
        )
        lbl_info.pack(side="left")

        btn_clear = ctk.CTkButton(
            top_bar,
            text="Vider la file",
            fg_color="#a31717",
            hover_color="#c42121",
            width=100,
            command=lambda: [qc.clear_queue(), self.rafraichir()][cite: 29]
        )
        btn_clear.pack(side="right")

        scroll = ctk.CTkScrollableFrame(tab, fg_color="transparent")
        scroll.pack(fill="both", expand=True)

        if not queue_songs:
            ctk.CTkLabel(scroll, text="La file d'attente est vide.", text_color="#a0a0a0").pack(pady=20)
            return

        for index, song in enumerate(queue_songs):
            row = ctk.CTkFrame(scroll, fg_color="#242424", height=45)
            row.pack(fill="x", pady=4, padx=5)

            titre = _get_val(song, 'title', 'name', 'filename', default='Titre inconnu')
            artiste = _get_val(song, 'artist', 'artist_name', default='Artiste inconnu')

            lbl_title = ctk.CTkLabel(row, text=f"{index + 1}. {titre} — {artiste}", font=ctk.CTkFont(size=13))
            lbl_title.pack(side="left", padx=10)

            # SUPPRIMER UN MORCEAU DE LA FILE D'ATTENTE
            btn_del = ctk.CTkButton(
                row,
                text="❌",
                width=30,
                height=26,
                fg_color="transparent",
                hover_color="#a31717",
                command=lambda s=song: self.supprimer_de_la_file(s)
            )
            btn_del.pack(side="right", padx=5)

            btn_play = ctk.CTkButton(
                row,
                text="▶",
                width=30,
                height=26,
                fg_color="#1DB954",
                text_color="#000",
                command=lambda s=song: pc.play_song(s)
            )
            btn_play.pack(side="right", padx=5)

    # --- Onglet Spécifique Playlists ---
    def _build_playlists_tab(self, tab, playlists_data):
        top_bar = ctk.CTkFrame(tab, fg_color="transparent")
        top_bar.pack(fill="x", pady=(0, 10))

        btn_creer = ctk.CTkButton(
            top_bar,
            text="+ Nouvelle Playlist",
            fg_color="#1DB954",
            hover_color="#17a34a",
            text_color="#000000",
            font=ctk.CTkFont(size=13, weight="bold"),
            command=self._dialog_creer_playlist
        )
        btn_creer.pack(side="left")

        scroll = ctk.CTkScrollableFrame(tab, fg_color="transparent")
        scroll.pack(fill="both", expand=True)

        n_cols = 3
        for i in range(n_cols):
            scroll.grid_columnconfigure(i, weight=1)

        for index, item in enumerate(playlists_data):
            row, col = divmod(index, n_cols)
            self._build_playlist_card(scroll, item).grid(
                row=row, column=col, padx=8, pady=8, sticky="nsew"
            )

    def _build_playlist_card(self, parent, item):
        nom_pl = item["nom_playlist"]
        chansons = item["object"]

        card = ctk.CTkFrame(parent, fg_color="#242424", corner_radius=10, height=220)

        cover = ctk.CTkFrame(card, fg_color="#2b5c3b", corner_radius=8, height=80)
        cover.pack(fill="x", padx=10, pady=(10, 6))

        lbl_icon = ctk.CTkLabel(cover, text="\U0001F4CB", font=ctk.CTkFont(size=30))
        lbl_icon.pack(expand=True)

        lbl_titre = ctk.CTkLabel(card, text=nom_pl, font=ctk.CTkFont(size=14, weight="bold"))
        lbl_titre.pack(padx=10, anchor="w")

        lbl_count = ctk.CTkLabel(card, text=f"{len(chansons)} chanson(s)", font=ctk.CTkFont(size=11), text_color="#a0a0a0")
        lbl_count.pack(padx=10, anchor="w")

        actions_frame = ctk.CTkFrame(card, fg_color="transparent")
        actions_frame.pack(fill="x", padx=6, pady=10, side="bottom")

        btn_ouvrir = ctk.CTkButton(
            actions_frame, text="Ouvrir", width=60, height=24,
            fg_color="#333333", hover_color="#444444",
            command=lambda n=nom_pl: self._dialog_voir_playlist(n)
        )
        btn_ouvrir.pack(side="left", padx=2)

        btn_renommer = ctk.CTkButton(
            actions_frame, text="✏️", width=30, height=24,
            fg_color="#333333", hover_color="#444444",
            command=lambda n=nom_pl: self._dialog_renommer_playlist(n)
        )
        btn_renommer.pack(side="left", padx=2)

        btn_suppr = ctk.CTkButton(
            actions_frame, text="🗑️", width=30, height=24,
            fg_color="#a31717", hover_color="#c42121",
            command=lambda n=nom_pl: self.supprimer_playlist(n)
        )
        btn_suppr.pack(side="right", padx=2)

        return card

    def _click(self, category, item):
        obj = item.get("object")
        if category not in ["Dossiers", "Playlists", "File d'attente"] and obj is not None:
            pc.play_song(obj)
            
        if self.on_item_click:
            self.on_item_click(category, item)

    # --- Actions et Boîtes de Dialogue des Playlists ---

    def _dialog_creer_playlist(self):
        dialog = ctk.CTkInputDialog(text="Entrez le nom de la nouvelle playlist :", title="Créer une Playlist")
        nom = dialog.get_input()
        if nom and nom.strip():
            nom = nom.strip()
            if nom not in self.playlists:
                self.playlists[nom] = []
                self.rafraichir()

    def _dialog_renommer_playlist(self, ancien_nom):
        dialog = ctk.CTkInputDialog(text=f"Nouveau nom pour '{ancien_nom}' :", title="Renommer la Playlist")
        nouveau_nom = dialog.get_input()
        if nouveau_nom and nouveau_nom.strip():
            nouveau_nom = nouveau_nom.strip()
            if nouveau_nom != ancien_nom:
                self.playlists[nouveau_nom] = self.playlists.pop(ancien_nom)
                self.rafraichir()

    def supprimer_playlist(self, nom_playlist):
        if nom_playlist in self.playlists:
            del self.playlists[nom_playlist]
            self.rafraichir()

    def _dialog_ajouter_chanson(self, song):
        if not self.playlists:
            return

        dialog = ctk.CTkToplevel(self)
        dialog.title("Ajouter à la playlist")
        dialog.geometry("300x250")
        dialog.attributes("-topmost", True)
        dialog.configure(fg_color="#1f1f1f")

        titre = _get_val(song, 'title', 'name', 'filename', default='Chanson')
        lbl = ctk.CTkLabel(dialog, text=f"Ajouter '{titre}' à :", font=ctk.CTkFont(size=12, weight="bold"), wraplength=260)
        lbl.pack(pady=12)

        scroll = ctk.CTkScrollableFrame(dialog, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=10, pady=5)

        for nom_pl in self.playlists.keys():
            btn = ctk.CTkButton(
                scroll,
                text=nom_pl,
                fg_color="#242424",
                hover_color="#1DB954",
                anchor="w",
                command=lambda n=nom_pl: [self._ajouter_chanson_a_playlist(song, n), dialog.destroy()]
            )
            btn.pack(fill="x", pady=3)

    def _ajouter_chanson_a_playlist(self, song, nom_playlist):
        if song not in self.playlists[nom_playlist]:
            self.playlists[nom_playlist].append(song)
            self.rafraichir()

    def _dialog_voir_playlist(self, nom_playlist):
        chansons = self.playlists.get(nom_playlist, [])

        dialog = ctk.CTkToplevel(self)
        dialog.title(f"Playlist : {nom_playlist}")
        dialog.geometry("450x400")
        dialog.attributes("-topmost", True)
        dialog.configure(fg_color="#1f1f1f")

        top = ctk.CTkFrame(dialog, fg_color="transparent")
        top.pack(fill="x", padx=15, pady=10)

        lbl = ctk.CTkLabel(top, text=nom_playlist, font=ctk.CTkFont(size=16, weight="bold"))
        lbl.pack(side="left")

        if chansons:
            btn_play_all = ctk.CTkButton(
                top, text="▶ Lire la playlist", width=110, fg_color="#1DB954", text_color="#000",
                command=lambda: [pc.play_song(chansons[0]), dialog.destroy()]
            )
            btn_play_all.pack(side="right")

        scroll = ctk.CTkScrollableFrame(dialog, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=15, pady=5)

        if not chansons:
            ctk.CTkLabel(scroll, text="Cette playlist est vide.", text_color="#a0a0a0").pack(pady=20)
            return

        for index, song in enumerate(chansons):
            row = ctk.CTkFrame(scroll, fg_color="#242424", height=40)
            row.pack(fill="x", pady=4)

            titre = _get_val(song, 'title', 'name', 'filename', default='Titre inconnu')
            artiste = _get_val(song, 'artist', 'artist_name', default='Artiste inconnu')

            lbl_info = ctk.CTkLabel(row, text=f"{titre} — {artiste}", font=ctk.CTkFont(size=12))
            lbl_info.pack(side="left", padx=10)

            btn_del = ctk.CTkButton(
                row, text="❌", width=28, height=24, fg_color="transparent", hover_color="#a31717",
                command=lambda s=song: [self.playlists[nom_playlist].remove(s), self.rafraichir(), dialog.destroy(), self._dialog_voir_playlist(nom_playlist)]
            )
            btn_del.pack(side="right", padx=5)

            btn_play = ctk.CTkButton(
                row, text="▶", width=28, height=24, fg_color="#1DB954", text_color="#000",
                command=lambda s=song: pc.play_song(s)
            )
            btn_play.pack(side="right", padx=5)