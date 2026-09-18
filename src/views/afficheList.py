"""
afficheList.py — CustomTkinter (Mélod'IA)

Affichage de toute la bibliothèque à partir du LibraryController :
    - Albums      -> library_controller.list_albums()
    - Artistes    -> library_controller.list_artists()
    - Morceaux    -> library_controller.list_songs()
    - Playlists   -> library_controller.list_playlists()
    - File        -> library_controller.list_queue()

Détails :
    - Morceaux d'un album    -> library_controller.list_songs_album(id_album)
    - Morceaux d'une playlist-> library_controller.list_song_playlist(id_playlist)
    - Morceaux d'un artiste  -> filtrage de list_songs() sur le nom de l'artiste

Remarque importante : player_controller.play_song() et queue_controller.add_song()
attendent un IDENTIFIANT (int), pas un objet morceau.
"""

import sys
import os

# Ajout du dossier parent au path Python (accès aux modules controllers / services)
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import customtkinter as ctk

from controllers.directory_controller import directory_controller
from controllers.library_controller import library_controller as lc
from controllers.player_controller import player_controller as pc
from controllers.queue_controller import queue_controller as qc

# playlist_controller / favori_controller n'exposent pas d'instance globale :
# on en crée une ici, de façon tolérante aux deux cas.
try:
    from controllers.playlist_controller import playlist_controller as plc  # type: ignore
except ImportError:
    from controllers.playlist_controller import PlaylistController
    plc = PlaylistController()

try:
    from controllers.favori_controller import favori_controller as fc  # type: ignore
except ImportError:
    from controllers.favori_controller import FavoriController
    fc = FavoriController()

from services.playlist_service import playlist_service
from services.library_service import library_service


# ---------------------------------------------------------------------------
# Palette
# ---------------------------------------------------------------------------
FOND        = "#181818"
FOND_CARTE  = "#242424"
FOND_HAUT   = "#1f1f1f"
VERT        = "#1DB954"
VERT_HOVER  = "#17a34a"
GRIS        = "#a0a0a0"
GRIS_FONCE  = "#333333"
ROUGE       = "#a31717"
ROUGE_HOVER = "#c42121"


# ---------------------------------------------------------------------------
# Fonctions utilitaires
# ---------------------------------------------------------------------------
def _get_val(obj, *cles, default=""):
    """Retourne la première clé / attribut non vide trouvé sur un objet ou un dict."""
    if obj is None:
        return default
    for cle in cles:
        valeur = obj.get(cle) if isinstance(obj, dict) else getattr(obj, cle, None)
        if valeur is not None and str(valeur).strip() != "":
            return str(valeur)
    return default


def _get_id(obj):
    """Retourne l'identifiant entier d'un objet (morceau, album, artiste, playlist) ou None."""
    if obj is None:
        return None
    brut = obj.get("id") if isinstance(obj, dict) else getattr(obj, "id", None)
    try:
        return int(brut)
    except (TypeError, ValueError):
        return None


def _format_duree(secondes):
    """Formate une durée en secondes vers 'm:ss'."""
    try:
        secondes = int(secondes)
    except (TypeError, ValueError):
        return "--:--"
    if secondes < 0:
        return "--:--"
    return f"{secondes // 60}:{secondes % 60:02d}"


def _appel_sur(objet, nom_methode, *args, defaut=None):
    """Appelle une méthode si elle existe, en neutralisant les erreurs (BD indisponible…)."""
    methode = getattr(objet, nom_methode, None)
    if not callable(methode):
        return defaut
    try:
        resultat = methode(*args)
    except Exception as erreur:
        print(f"[afficheList] Erreur {nom_methode}: {erreur}")
        return defaut
    return resultat


def _liste(resultat):
    """Normalise un résultat de contrôleur en liste."""
    if resultat is None:
        return []
    if isinstance(resultat, list):
        return resultat
    if isinstance(resultat, (tuple, set)):
        return list(resultat)
    return []


# ---------------------------------------------------------------------------
# Composant principal
# ---------------------------------------------------------------------------
class ListDisplay(ctk.CTkFrame):
    """Zone centrale du lecteur : onglets Albums / Artistes / Morceaux / Playlists / File."""

    ONGLETS = ["Albums", "Artistes", "Morceaux", "Playlists", "File d'attente"]

    def __init__(self, master, on_item_click=None, **kwargs):
        super().__init__(master, fg_color=FOND, corner_radius=0, **kwargs)
        self.on_item_click = on_item_click

        # Mode d'affichage des morceaux : "liste" (tableau) ou "grille" (cartes)
        self.view_mode_morceaux = "liste"

        # Texte de recherche appliqué à l'onglet Morceaux
        self.recherche = ""

        # Données rechargées à chaque rafraîchissement
        self.albums = []
        self.artistes = []
        self.morceaux = []
        self.playlists = []
        self.file_attente = []

        # Conteneur d'onglets
        self.tabview = ctk.CTkTabview(
            self,
            fg_color=FOND,
            segmented_button_fg_color="#242424",
            segmented_button_selected_color=VERT,
            segmented_button_selected_hover_color=VERT_HOVER,
        )
        self.tabview.pack(fill="both", expand=True, padx=16, pady=16)

        self.tabs_name = list(self.ONGLETS)
        for nom in self.tabs_name:
            self.tabview.add(nom)

        self.rafraichir()

    # -- API publique utilisée par main.py ---------------------------------

    def on_import_complete(self, onglet):
        """Appelé après un import de répertoire : on scanne puis on recharge."""
        self.scanner_et_rafraichir()
        self.changer_onglet(onglet)

    def changer_onglet(self, nom_onglet):
        if nom_onglet in self.tabs_name:
            self.tabview.set(nom_onglet)

    def scanner_et_rafraichir(self):
        """Relance l'indexation des répertoires puis recharge l'affichage."""
        _appel_sur(directory_controller, "scan_all")
        self.rafraichir()

    # -- Chargement des données -------------------------------------------

    def charger_donnees(self):
        """Récupère l'intégralité de la bibliothèque via le LibraryController."""
        self.morceaux = _liste(_appel_sur(lc, "list_songs", defaut=[]))
        if not self.morceaux:
            self.morceaux = _liste(_appel_sur(library_service, "list_songs", defaut=[]))

        self.albums = _liste(_appel_sur(lc, "list_albums", defaut=[]))
        if not self.albums:
            self.albums = _liste(_appel_sur(library_service, "list_albums", defaut=[]))

        self.artistes = _liste(_appel_sur(lc, "list_artists", defaut=[]))
        if not self.artistes:
            self.artistes = _liste(_appel_sur(library_service, "list_artists", defaut=[]))

        self.playlists = _liste(_appel_sur(lc, "list_playlists", defaut=[]))
        if not self.playlists:
            self.playlists = _liste(_appel_sur(library_service, "list_playlists", defaut=[]))

        self.file_attente = _liste(_appel_sur(lc, "list_queue", defaut=[]))

    def morceaux_filtres(self):
        """Applique le filtre de recherche sur les morceaux."""
        if not self.recherche:
            return self.morceaux
        motif = self.recherche.lower()
        resultat = []
        for song in self.morceaux:
            texte = " ".join([
                _get_val(song, "title", "titre"),
                _get_val(song, "artists", "artist"),
                _get_val(song, "album"),
            ]).lower()
            if motif in texte:
                resultat.append(song)
        return resultat

    def morceaux_de_album(self, id_album):
        songs = _liste(_appel_sur(lc, "list_songs_album", id_album, defaut=[]))
        if songs:
            return songs
        # Repli : filtrage sur le titre d'album des morceaux déjà chargés
        return [s for s in self.morceaux if _get_id(s) is not None]

    def morceaux_de_artiste(self, nom_artiste):
        """Aucune méthode dédiée dans le contrôleur : on filtre la liste des morceaux."""
        nom = (nom_artiste or "").lower().strip()
        if not nom:
            return []
        return [
            song for song in self.morceaux
            if nom in _get_val(song, "artists", "artist", default="").lower()
        ]

    def morceaux_de_playlist(self, id_playlist):
        return _liste(_appel_sur(lc, "list_song_playlist", id_playlist, defaut=[]))

    # -- Rafraîchissement --------------------------------------------------

    def rafraichir(self):
        """Recharge les données et reconstruit tous les onglets."""
        self.charger_donnees()

        for nom in self.tabs_name:
            onglet = self.tabview.tab(nom)
            for widget in onglet.winfo_children():
                widget.destroy()

            if nom == "Albums":
                self._build_albums_tab(onglet)
            elif nom == "Artistes":
                self._build_artistes_tab(onglet)
            elif nom == "Morceaux":
                self._build_morceaux_tab(onglet)
            elif nom == "Playlists":
                self._build_playlists_tab(onglet)
            elif nom == "File d'attente":
                self._build_queue_tab(onglet)

    # -- Barre d'en-tête commune ------------------------------------------

    def _barre_titre(self, parent, texte, compteur=None):
        barre = ctk.CTkFrame(parent, fg_color="transparent")
        barre.pack(fill="x", pady=(0, 8))

        libelle = texte if compteur is None else f"{texte}  ({compteur})"
        ctk.CTkLabel(
            barre, text=libelle, font=ctk.CTkFont(size=16, weight="bold")
        ).pack(side="left")

        ctk.CTkButton(
            barre, text="\u21bb Actualiser", width=110, height=28,
            fg_color=GRIS_FONCE, hover_color="#444444",
            command=self.scanner_et_rafraichir
        ).pack(side="right", padx=(6, 0))

        return barre

    def _zone_vide(self, parent, message):
        ctk.CTkLabel(parent, text=message, text_color=GRIS).pack(pady=30)

    # -- Onglet ALBUMS -----------------------------------------------------

    def _build_albums_tab(self, onglet):
        self._barre_titre(onglet, "Albums", len(self.albums))

        scroll = ctk.CTkScrollableFrame(onglet, fg_color="transparent")
        scroll.pack(fill="both", expand=True)

        if not self.albums:
            self._zone_vide(scroll, "Aucun album. Importez un répertoire de musique.")
            return

        n_cols = 4
        for i in range(n_cols):
            scroll.grid_columnconfigure(i, weight=1)

        for index, album in enumerate(self.albums):
            ligne, colonne = divmod(index, n_cols)
            self._carte_album(scroll, album).grid(
                row=ligne, column=colonne, padx=8, pady=8, sticky="nsew"
            )

    def _carte_album(self, parent, album):
        titre = _get_val(album, "title", "titre", default="Album inconnu")
        artistes = _get_val(album, "artists", "artist", default="Artiste inconnu")
        annee = _get_val(album, "release_year", "annee_sortie", default="")
        id_album = _get_id(album)

        carte = ctk.CTkFrame(parent, fg_color=FOND_CARTE, corner_radius=10, width=175, height=215)
        carte.grid_propagate(False)

        pochette = ctk.CTkFrame(carte, fg_color=VERT, corner_radius=8, width=155, height=95)
        pochette.pack(padx=10, pady=(10, 6))
        pochette.pack_propagate(False)
        ctk.CTkLabel(pochette, text="\U0001F4BF", font=ctk.CTkFont(size=34),
                     text_color="#000000").pack(expand=True)

        ctk.CTkLabel(carte, text=titre, font=ctk.CTkFont(size=13, weight="bold"),
                     anchor="w", wraplength=150).pack(padx=10, anchor="w")
        sous_titre = artistes if not annee else f"{artistes} • {annee}"
        ctk.CTkLabel(carte, text=sous_titre, font=ctk.CTkFont(size=11),
                     text_color=GRIS, anchor="w", wraplength=150).pack(padx=10, anchor="w")

        actions = ctk.CTkFrame(carte, fg_color="transparent")
        actions.pack(fill="x", padx=6, pady=8, side="bottom")

        ctk.CTkButton(
            actions, text="Voir", width=60, height=24,
            fg_color=GRIS_FONCE, hover_color="#444444",
            command=lambda: self._dialog_morceaux(f"Album : {titre}", self.morceaux_de_album(id_album))
        ).pack(side="left", padx=2)

        ctk.CTkButton(
            actions, text="\u25B6 Lire", width=65, height=24,
            fg_color=VERT, hover_color=VERT_HOVER, text_color="#000000",
            command=lambda: self.lire_ensemble(self.morceaux_de_album(id_album))
        ).pack(side="right", padx=2)

        item = {"titre": titre, "sous_titre": sous_titre, "object": album}
        for widget in (carte, pochette):
            widget.bind("<Button-1>", lambda e: self._click("Albums", item))

        return carte

    # -- Onglet ARTISTES ---------------------------------------------------

    def _build_artistes_tab(self, onglet):
        self._barre_titre(onglet, "Artistes", len(self.artistes))

        scroll = ctk.CTkScrollableFrame(onglet, fg_color="transparent")
        scroll.pack(fill="both", expand=True)

        if not self.artistes:
            self._zone_vide(scroll, "Aucun artiste. Importez un répertoire de musique.")
            return

        n_cols = 4
        for i in range(n_cols):
            scroll.grid_columnconfigure(i, weight=1)

        for index, artiste in enumerate(self.artistes):
            ligne, colonne = divmod(index, n_cols)
            self._carte_artiste(scroll, artiste).grid(
                row=ligne, column=colonne, padx=8, pady=8, sticky="nsew"
            )

    def _carte_artiste(self, parent, artiste):
        nom = _get_val(artiste, "name", "nom", "nom_scene", default="Artiste inconnu")
        ses_morceaux = self.morceaux_de_artiste(nom)

        carte = ctk.CTkFrame(parent, fg_color=FOND_CARTE, corner_radius=10, width=175, height=215)
        carte.grid_propagate(False)

        rond = ctk.CTkFrame(carte, fg_color="#2b5c3b", corner_radius=50, width=95, height=95)
        rond.pack(padx=10, pady=(12, 6))
        rond.pack_propagate(False)
        ctk.CTkLabel(rond, text="\U0001F3A4", font=ctk.CTkFont(size=32)).pack(expand=True)

        ctk.CTkLabel(carte, text=nom, font=ctk.CTkFont(size=13, weight="bold"),
                     wraplength=150).pack(padx=10)
        ctk.CTkLabel(carte, text=f"{len(ses_morceaux)} morceau(x)",
                     font=ctk.CTkFont(size=11), text_color=GRIS).pack(padx=10)

        actions = ctk.CTkFrame(carte, fg_color="transparent")
        actions.pack(fill="x", padx=6, pady=8, side="bottom")

        ctk.CTkButton(
            actions, text="Voir", width=60, height=24,
            fg_color=GRIS_FONCE, hover_color="#444444",
            command=lambda: self._dialog_morceaux(f"Artiste : {nom}", self.morceaux_de_artiste(nom))
        ).pack(side="left", padx=2)

        ctk.CTkButton(
            actions, text="\u25B6 Lire", width=65, height=24,
            fg_color=VERT, hover_color=VERT_HOVER, text_color="#000000",
            command=lambda: self.lire_ensemble(self.morceaux_de_artiste(nom))
        ).pack(side="right", padx=2)

        item = {"titre": nom, "sous_titre": f"{len(ses_morceaux)} morceau(x)", "object": artiste}
        for widget in (carte, rond):
            widget.bind("<Button-1>", lambda e: self._click("Artistes", item))

        return carte

    # -- Onglet MORCEAUX ---------------------------------------------------

    def _build_morceaux_tab(self, onglet):
        barre = ctk.CTkFrame(onglet, fg_color="transparent")
        barre.pack(fill="x", pady=(0, 8))

        ctk.CTkLabel(
            barre, text=f"Morceaux  ({len(self.morceaux)})",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(side="left")

        bouton_mode = ctk.CTkSegmentedButton(
            barre, values=["Liste", "Grille"],
            selected_color=VERT, selected_hover_color=VERT_HOVER,
            command=self._changer_mode_vue_morceaux
        )
        bouton_mode.set("Liste" if self.view_mode_morceaux == "liste" else "Grille")
        bouton_mode.pack(side="right", padx=(6, 0))

        champ = ctk.CTkEntry(barre, placeholder_text="Rechercher un titre, artiste, album…", width=240)
        if self.recherche:
            champ.insert(0, self.recherche)
        champ.pack(side="right", padx=6)
        champ.bind("<Return>", lambda e: self._appliquer_recherche(champ.get()))

        ctk.CTkButton(
            barre, text="\U0001F50D", width=34, height=28,
            fg_color=GRIS_FONCE, hover_color="#444444",
            command=lambda: self._appliquer_recherche(champ.get())
        ).pack(side="right")

        items = self.morceaux_filtres()

        if self.view_mode_morceaux == "liste":
            self._vue_tableau_morceaux(onglet, items)
        else:
            self._vue_grille_morceaux(onglet, items)

    def _appliquer_recherche(self, texte):
        self.recherche = (texte or "").strip()
        self.rafraichir()
        self.changer_onglet("Morceaux")

    def _changer_mode_vue_morceaux(self, mode):
        self.view_mode_morceaux = "liste" if mode == "Liste" else "grille"
        self.rafraichir()
        self.changer_onglet("Morceaux")

    def _vue_tableau_morceaux(self, parent, morceaux):
        scroll = ctk.CTkScrollableFrame(parent, fg_color="transparent")
        scroll.pack(fill="both", expand=True)

        if not morceaux:
            self._zone_vide(scroll, "Aucun morceau trouvé.")
            return

        entete = ctk.CTkFrame(scroll, fg_color=FOND_HAUT, height=30)
        entete.pack(fill="x", pady=(0, 5))
        entete.pack_propagate(False)

        police_entete = ctk.CTkFont(size=11, weight="bold")
        ctk.CTkLabel(entete, text="", width=30).pack(side="left", padx=5)
        ctk.CTkLabel(entete, text="#", width=35, anchor="w", text_color="#888888",
                     font=police_entete).pack(side="left")
        ctk.CTkLabel(entete, text="Titre", anchor="w", text_color="#888888",
                     font=police_entete).pack(side="left", fill="x", expand=True, padx=5)
        ctk.CTkLabel(entete, text="Artiste", anchor="w", width=160, text_color="#888888",
                     font=police_entete).pack(side="left", padx=5)
        ctk.CTkLabel(entete, text="Album", anchor="w", width=150, text_color="#888888",
                     font=police_entete).pack(side="left", padx=5)
        ctk.CTkLabel(entete, text="Durée", width=55, text_color="#888888",
                     font=police_entete).pack(side="left")
        ctk.CTkLabel(entete, text="Actions", width=110, text_color="#888888",
                     font=police_entete).pack(side="right", padx=10)

        for index, song in enumerate(morceaux):
            self._ligne_morceau(scroll, song, index)

    def _ligne_morceau(self, parent, song, index):
        id_song = _get_id(song)
        titre = _get_val(song, "title", "titre", default="Titre inconnu")
        artiste = _get_val(song, "artists", "artist", default="Artiste inconnu")
        album = _get_val(song, "album", default="Album inconnu")
        duree = _format_duree(getattr(song, "duration", None))
        favori = bool(getattr(song, "favori", False))

        ligne = ctk.CTkFrame(parent, fg_color=FOND if index % 2 == 0 else "#202020", height=38)
        ligne.pack(fill="x", pady=1)
        ligne.pack_propagate(False)

        icone = ctk.CTkLabel(ligne, text="\U0001F3B5", width=30, text_color=VERT,
                             font=ctk.CTkFont(size=14))
        icone.pack(side="left", padx=5)

        numero = ctk.CTkLabel(ligne, text=str(index + 1), width=35, anchor="w",
                              text_color=GRIS, font=ctk.CTkFont(size=12))
        numero.pack(side="left")

        lbl_titre = ctk.CTkLabel(ligne, text=titre, anchor="w",
                                 font=ctk.CTkFont(size=12, weight="bold"))
        lbl_titre.pack(side="left", fill="x", expand=True, padx=5)

        lbl_artiste = ctk.CTkLabel(ligne, text=artiste, width=160, anchor="w",
                                   text_color="#cccccc", font=ctk.CTkFont(size=12))
        lbl_artiste.pack(side="left", padx=5)

        lbl_album = ctk.CTkLabel(ligne, text=album, width=150, anchor="w",
                                 text_color="#888888", font=ctk.CTkFont(size=11))
        lbl_album.pack(side="left", padx=5)

        lbl_duree = ctk.CTkLabel(ligne, text=duree, width=55, text_color="#888888",
                                 font=ctk.CTkFont(size=11))
        lbl_duree.pack(side="left")

        actions = ctk.CTkFrame(ligne, fg_color="transparent")
        actions.pack(side="right", padx=5)

        ctk.CTkButton(
            actions, text="\u25B6", width=26, height=24,
            fg_color=VERT, hover_color=VERT_HOVER, text_color="#000000",
            command=lambda: self.lire_morceau(song)
        ).pack(side="left", padx=2)

        ctk.CTkButton(
            actions, text="\u2764" if favori else "\u2661", width=26, height=24,
            fg_color=ROUGE if favori else GRIS_FONCE, hover_color="#444444",
            command=lambda: self.basculer_favori(song)
        ).pack(side="left", padx=2)

        ctk.CTkButton(
            actions, text="+", width=26, height=24,
            fg_color=GRIS_FONCE, hover_color="#444444",
            command=lambda: self.ajouter_a_la_file(song)
        ).pack(side="left", padx=2)

        ctk.CTkButton(
            actions, text="\u2261", width=26, height=24,
            fg_color=GRIS_FONCE, hover_color="#444444",
            command=lambda: self._dialog_ajouter_a_playlist(song)
        ).pack(side="left", padx=2)

        item = {"titre": titre, "sous_titre": artiste, "album": album, "object": song}
        for widget in (ligne, icone, numero, lbl_titre, lbl_artiste, lbl_album, lbl_duree):
            widget.bind("<Double-Button-1>", lambda e: self._click("Morceaux", item))

        return ligne

    def _vue_grille_morceaux(self, parent, morceaux):
        scroll = ctk.CTkScrollableFrame(parent, fg_color="transparent")
        scroll.pack(fill="both", expand=True)

        if not morceaux:
            self._zone_vide(scroll, "Aucun morceau trouvé.")
            return

        n_cols = 4
        for i in range(n_cols):
            scroll.grid_columnconfigure(i, weight=1)

        for index, song in enumerate(morceaux):
            ligne, colonne = divmod(index, n_cols)
            self._carte_morceau(scroll, song).grid(
                row=ligne, column=colonne, padx=8, pady=8, sticky="nsew"
            )

    def _carte_morceau(self, parent, song):
        titre = _get_val(song, "title", "titre", default="Titre inconnu")
        artiste = _get_val(song, "artists", "artist", default="Artiste inconnu")
        album = _get_val(song, "album", default="Album inconnu")
        duree = _format_duree(getattr(song, "duration", None))

        carte = ctk.CTkFrame(parent, fg_color=FOND_CARTE, corner_radius=10, width=175, height=225)
        carte.grid_propagate(False)

        pochette = ctk.CTkFrame(carte, fg_color=VERT, corner_radius=8, width=155, height=90)
        pochette.pack(padx=10, pady=(10, 6))
        pochette.pack_propagate(False)
        ctk.CTkLabel(pochette, text="\U0001F3B5", font=ctk.CTkFont(size=32),
                     text_color="#000000").pack(expand=True)

        ctk.CTkLabel(carte, text=titre, font=ctk.CTkFont(size=13, weight="bold"),
                     anchor="w", wraplength=150).pack(padx=10, anchor="w")
        ctk.CTkLabel(carte, text=f"{artiste} • {duree}", font=ctk.CTkFont(size=11),
                     text_color=GRIS, anchor="w", wraplength=150).pack(padx=10, anchor="w")
        ctk.CTkLabel(carte, text=album, font=ctk.CTkFont(size=10),
                     text_color="#777777", anchor="w", wraplength=150).pack(padx=10, anchor="w")

        actions = ctk.CTkFrame(carte, fg_color="transparent")
        actions.pack(fill="x", padx=6, pady=8, side="bottom")

        ctk.CTkButton(
            actions, text="\u25B6", width=32, height=24,
            fg_color=VERT, hover_color=VERT_HOVER, text_color="#000000",
            command=lambda: self.lire_morceau(song)
        ).pack(side="left", padx=2)

        ctk.CTkButton(
            actions, text="+ Playlist", width=68, height=24,
            fg_color=GRIS_FONCE, hover_color="#444444",
            font=ctk.CTkFont(size=10, weight="bold"),
            command=lambda: self._dialog_ajouter_a_playlist(song)
        ).pack(side="left", padx=2)

        ctk.CTkButton(
            actions, text="+ File", width=52, height=24,
            fg_color=GRIS_FONCE, hover_color="#444444",
            font=ctk.CTkFont(size=10, weight="bold"),
            command=lambda: self.ajouter_a_la_file(song)
        ).pack(side="right", padx=2)

        item = {"titre": titre, "sous_titre": artiste, "album": album, "object": song}
        for widget in (carte, pochette):
            widget.bind("<Button-1>", lambda e: self._click("Morceaux", item))

        return carte

    # -- Onglet PLAYLISTS --------------------------------------------------

    def _build_playlists_tab(self, onglet):
        barre = ctk.CTkFrame(onglet, fg_color="transparent")
        barre.pack(fill="x", pady=(0, 8))

        ctk.CTkLabel(
            barre, text=f"Playlists  ({len(self.playlists)})",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(side="left")

        ctk.CTkButton(
            barre, text="+ Nouvelle playlist", fg_color=VERT, hover_color=VERT_HOVER,
            text_color="#000000", font=ctk.CTkFont(size=13, weight="bold"),
            command=self._dialog_creer_playlist
        ).pack(side="right")

        scroll = ctk.CTkScrollableFrame(onglet, fg_color="transparent")
        scroll.pack(fill="both", expand=True)

        if not self.playlists:
            self._zone_vide(scroll, "Aucune playlist. Créez-en une avec le bouton ci-dessus.")
            return

        n_cols = 3
        for i in range(n_cols):
            scroll.grid_columnconfigure(i, weight=1)

        for index, playlist in enumerate(self.playlists):
            ligne, colonne = divmod(index, n_cols)
            self._carte_playlist(scroll, playlist).grid(
                row=ligne, column=colonne, padx=8, pady=8, sticky="nsew"
            )

    def _carte_playlist(self, parent, playlist):
        nom = _get_val(playlist, "name", "nom", default="Playlist")
        id_playlist = _get_id(playlist)
        chansons = self.morceaux_de_playlist(id_playlist) if id_playlist is not None else []

        carte = ctk.CTkFrame(parent, fg_color=FOND_CARTE, corner_radius=10, height=215)

        pochette = ctk.CTkFrame(carte, fg_color="#2b5c3b", corner_radius=8, height=85)
        pochette.pack(fill="x", padx=10, pady=(10, 6))
        pochette.pack_propagate(False)
        ctk.CTkLabel(pochette, text="\U0001F4CB", font=ctk.CTkFont(size=30)).pack(expand=True)

        ctk.CTkLabel(carte, text=nom, font=ctk.CTkFont(size=14, weight="bold"),
                     anchor="w").pack(padx=10, anchor="w")
        ctk.CTkLabel(carte, text=f"{len(chansons)} morceau(x)", font=ctk.CTkFont(size=11),
                     text_color=GRIS, anchor="w").pack(padx=10, anchor="w")

        actions = ctk.CTkFrame(carte, fg_color="transparent")
        actions.pack(fill="x", padx=6, pady=10, side="bottom")

        ctk.CTkButton(
            actions, text="Ouvrir", width=58, height=24,
            fg_color=GRIS_FONCE, hover_color="#444444",
            command=lambda: self._dialog_morceaux(
                f"Playlist : {nom}", self.morceaux_de_playlist(id_playlist),
                id_playlist=id_playlist
            )
        ).pack(side="left", padx=2)

        ctk.CTkButton(
            actions, text="\u25B6", width=32, height=24,
            fg_color=VERT, hover_color=VERT_HOVER, text_color="#000000",
            command=lambda: self.lire_playlist(id_playlist)
        ).pack(side="left", padx=2)

        ctk.CTkButton(
            actions, text="\u270F", width=30, height=24,
            fg_color=GRIS_FONCE, hover_color="#444444",
            command=lambda: self._dialog_renommer_playlist(id_playlist, nom)
        ).pack(side="left", padx=2)

        ctk.CTkButton(
            actions, text="\U0001F5D1", width=30, height=24,
            fg_color=ROUGE, hover_color=ROUGE_HOVER,
            command=lambda: self.supprimer_playlist(id_playlist)
        ).pack(side="right", padx=2)

        item = {"titre": nom, "sous_titre": f"{len(chansons)} morceau(x)", "object": playlist}
        for widget in (carte, pochette):
            widget.bind("<Button-1>", lambda e: self._click("Playlists", item))

        return carte

    # -- Onglet FILE D'ATTENTE --------------------------------------------

    def _build_queue_tab(self, onglet):
        barre = ctk.CTkFrame(onglet, fg_color="transparent")
        barre.pack(fill="x", pady=(0, 10))

        ctk.CTkLabel(
            barre, text=f"File d'attente  ({len(self.file_attente)} morceau(x))",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(side="left")

        ctk.CTkButton(
            barre, text="Vider la file", fg_color=ROUGE, hover_color=ROUGE_HOVER, width=110,
            command=self.vider_la_file
        ).pack(side="right")

        scroll = ctk.CTkScrollableFrame(onglet, fg_color="transparent")
        scroll.pack(fill="both", expand=True)

        if not self.file_attente:
            self._zone_vide(scroll, "La file d'attente est vide.")
            return

        for index, song in enumerate(self.file_attente):
            titre = _get_val(song, "title", "titre", default="Titre inconnu")
            artiste = _get_val(song, "artists", "artist", default="Artiste inconnu")
            duree = _format_duree(getattr(song, "duration", None))

            ligne = ctk.CTkFrame(scroll, fg_color=FOND_CARTE, height=44)
            ligne.pack(fill="x", pady=4, padx=5)
            ligne.pack_propagate(False)

            ctk.CTkLabel(
                ligne, text=f"\U0001F3B5 {index + 1}. {titre} — {artiste}",
                font=ctk.CTkFont(size=13), anchor="w"
            ).pack(side="left", padx=10)

            ctk.CTkButton(
                ligne, text="\u274C", width=30, height=26,
                fg_color="transparent", hover_color=ROUGE,
                command=lambda s=song: self.supprimer_de_la_file(s)
            ).pack(side="right", padx=5)

            ctk.CTkButton(
                ligne, text="\u25B6", width=30, height=26,
                fg_color=VERT, hover_color=VERT_HOVER, text_color="#000000",
                command=lambda s=song: self.lire_morceau(s)
            ).pack(side="right", padx=5)

            ctk.CTkLabel(ligne, text=duree, width=55, text_color="#888888",
                         font=ctk.CTkFont(size=11)).pack(side="right", padx=5)

    # -- Actions lecture / file / favoris ---------------------------------

    def lire_morceau(self, song):
        """player_controller.play_song attend un identifiant entier."""
        id_song = _get_id(song)
        if id_song is None:
            return
        _appel_sur(qc, "add_song", id_song)
        _appel_sur(pc, "play_song", id_song)
        self._notifier_click(song)

    def lire_ensemble(self, morceaux):
        """Remplit la file avec une liste de morceaux puis lance la lecture du premier."""
        morceaux = [s for s in morceaux if _get_id(s) is not None]
        if not morceaux:
            return
        _appel_sur(qc, "clear_queue")
        for song in morceaux:
            _appel_sur(qc, "add_song", _get_id(song))
        _appel_sur(pc, "play_song", _get_id(morceaux[0]))
        self.rafraichir()

    def lire_playlist(self, id_playlist):
        if id_playlist is None:
            return
        _appel_sur(plc, "play", id_playlist, None)
        self.rafraichir()

    def ajouter_a_la_file(self, song):
        id_song = _get_id(song)
        if id_song is None:
            return
        _appel_sur(qc, "add_song", id_song)
        self.rafraichir()

    def supprimer_de_la_file(self, song):
        id_song = _get_id(song)
        if id_song is None:
            return
        _appel_sur(qc, "remove_song", id_song)
        self.rafraichir()

    def vider_la_file(self):
        _appel_sur(qc, "clear_queue")
        self.rafraichir()

    def basculer_favori(self, song):
        id_song = _get_id(song)
        if id_song is None:
            return
        if bool(getattr(song, "favori", False)):
            _appel_sur(fc, "remove_favori", id_song)
        else:
            _appel_sur(fc, "add_favori", id_song)
        self.rafraichir()

    # -- Actions playlists -------------------------------------------------

    def _dialog_creer_playlist(self):
        dialogue = ctk.CTkInputDialog(
            text="Nom de la nouvelle playlist :", title="Créer une playlist"
        )
        nom = (dialogue.get_input() or "").strip()
        if nom:
            _appel_sur(plc, "create", nom)
            self.rafraichir()
            self.changer_onglet("Playlists")

    def _dialog_renommer_playlist(self, id_playlist, ancien_nom):
        if id_playlist is None:
            return
        dialogue = ctk.CTkInputDialog(
            text=f"Nouveau nom pour « {ancien_nom} » :", title="Renommer la playlist"
        )
        nouveau = (dialogue.get_input() or "").strip()
        if nouveau and nouveau != ancien_nom:
            _appel_sur(playlist_service, "rename_playlist", id_playlist, nouveau)
            self.rafraichir()
            self.changer_onglet("Playlists")

    def supprimer_playlist(self, id_playlist):
        if id_playlist is None:
            return
        _appel_sur(plc, "remove", id_playlist)
        self.rafraichir()
        self.changer_onglet("Playlists")

    def _dialog_ajouter_a_playlist(self, song):
        id_song = _get_id(song)
        if id_song is None:
            return

        playlists = _liste(_appel_sur(lc, "list_playlists", defaut=[]))
        if not playlists:
            self._dialog_creer_playlist()
            playlists = _liste(_appel_sur(lc, "list_playlists", defaut=[]))
            if not playlists:
                return

        fenetre = ctk.CTkToplevel(self)
        fenetre.title("Ajouter à une playlist")
        fenetre.geometry("320x300")
        fenetre.attributes("-topmost", True)
        fenetre.configure(fg_color="#1f1f1f")

        titre = _get_val(song, "title", "titre", default="Morceau")
        ctk.CTkLabel(
            fenetre, text=f"Ajouter « {titre} » à :",
            font=ctk.CTkFont(size=12, weight="bold"), wraplength=280
        ).pack(pady=12)

        scroll = ctk.CTkScrollableFrame(fenetre, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=10, pady=5)

        for playlist in playlists:
            nom = _get_val(playlist, "name", "nom", default="Playlist")
            id_playlist = _get_id(playlist)
            ctk.CTkButton(
                scroll, text=nom, fg_color=FOND_CARTE, hover_color=VERT, anchor="w",
                command=lambda p=id_playlist: [
                    self.ajouter_morceau_a_playlist(p, id_song), fenetre.destroy()
                ]
            ).pack(fill="x", pady=3)

    def ajouter_morceau_a_playlist(self, id_playlist, id_song):
        if id_playlist is None or id_song is None:
            return
        _appel_sur(plc, "add_song", id_playlist, id_song)
        self.rafraichir()

    def retirer_morceau_de_playlist(self, id_playlist, id_song):
        if id_playlist is None or id_song is None:
            return
        _appel_sur(plc, "remove_song", id_playlist, id_song)
        self.rafraichir()

    # -- Fenêtre de détail (morceaux d'un album / artiste / playlist) -----

    def _dialog_morceaux(self, titre_fenetre, morceaux, id_playlist=None):
        fenetre = ctk.CTkToplevel(self)
        fenetre.title(titre_fenetre)
        fenetre.geometry("560x430")
        fenetre.attributes("-topmost", True)
        fenetre.configure(fg_color="#1f1f1f")

        haut = ctk.CTkFrame(fenetre, fg_color="transparent")
        haut.pack(fill="x", padx=15, pady=10)

        ctk.CTkLabel(haut, text=titre_fenetre,
                     font=ctk.CTkFont(size=16, weight="bold"), wraplength=380).pack(side="left")

        if morceaux:
            ctk.CTkButton(
                haut, text="\u25B6 Tout lire", width=105,
                fg_color=VERT, hover_color=VERT_HOVER, text_color="#000000",
                command=lambda: [self.lire_ensemble(morceaux), fenetre.destroy()]
            ).pack(side="right")

        scroll = ctk.CTkScrollableFrame(fenetre, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=15, pady=5)

        if not morceaux:
            ctk.CTkLabel(scroll, text="Aucun morceau.", text_color=GRIS).pack(pady=20)
            return

        for index, song in enumerate(morceaux):
            id_song = _get_id(song)
            titre = _get_val(song, "title", "titre", default="Titre inconnu")
            artiste = _get_val(song, "artists", "artist", default="Artiste inconnu")
            duree = _format_duree(getattr(song, "duration", None))

            ligne = ctk.CTkFrame(scroll, fg_color=FOND_CARTE, height=40)
            ligne.pack(fill="x", pady=4)
            ligne.pack_propagate(False)

            ctk.CTkLabel(
                ligne, text=f"\U0001F3B5 {index + 1}. {titre} — {artiste}",
                font=ctk.CTkFont(size=12), anchor="w"
            ).pack(side="left", padx=10)

            if id_playlist is not None:
                ctk.CTkButton(
                    ligne, text="\u274C", width=28, height=24,
                    fg_color="transparent", hover_color=ROUGE,
                    command=lambda s=id_song: [
                        self.retirer_morceau_de_playlist(id_playlist, s), fenetre.destroy()
                    ]
                ).pack(side="right", padx=4)
            else:
                ctk.CTkButton(
                    ligne, text="+", width=28, height=24,
                    fg_color=GRIS_FONCE, hover_color="#444444",
                    command=lambda s=song: self.ajouter_a_la_file(s)
                ).pack(side="right", padx=4)

            ctk.CTkButton(
                ligne, text="\u25B6", width=28, height=24,
                fg_color=VERT, hover_color=VERT_HOVER, text_color="#000000",
                command=lambda s=song: self.lire_morceau(s)
            ).pack(side="right", padx=4)

            ctk.CTkLabel(ligne, text=duree, width=50, text_color="#888888",
                         font=ctk.CTkFont(size=11)).pack(side="right", padx=4)

    # -- Callbacks ---------------------------------------------------------

    def _click(self, categorie, item):
        """Clic sur un élément : lecture directe pour un morceau, notification sinon."""
        if categorie == "Morceaux":
            self.lire_morceau(item.get("object"))
            return
        self._notifier(categorie, item)

    def _notifier_click(self, song):
        item = {
            "titre": _get_val(song, "title", "titre", default="Titre inconnu"),
            "sous_titre": _get_val(song, "artists", "artist", default="Artiste inconnu"),
            "object": song,
        }
        self._notifier("Morceaux", item)

    def _notifier(self, categorie, item):
        if self.on_item_click:
            try:
                self.on_item_click(categorie, item)
            except Exception as erreur:
                print(f"[afficheList] Erreur on_item_click: {erreur}")