import customtkinter as ctk
from views.sidebar_new import Sidebar
from views.acceuil_new import Acceuil
from views.queue_view_new import QueueView
from views.favorites_view_new import FavoritesView
from views.playlists_view_new import PlaylistsView
from views.directories_view_new import DirectoriesView
from views.settings_view_new import SettingsView
from views.player_bar import PlayerBar
from views.lyrics_view import LyricsView

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # Configuration de la fenêtre
        self.title("Melod'IA")
        self.geometry("1080x620+20+20")
        
        # Configuration des couleurs et du thème
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        self.COLOR_NAV = "#2c3e50"
        self.COLOR_BTN_DEFAULT = "#34495e"
        self.COLOR_BTN_ACTIVE = "#1abc9c"
        
        # Grid configuration
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        
        #############################
        # Sidebar
        #############################
        self.sidebar = Sidebar(self, self.toogle_sidebar, self.changer_page)
        self.sidebar.grid(row=0, column=0, sticky="nsew", rowspan=2)
        
        #############################
        # Main Content
        #############################
        self.main = ctk.CTkFrame(self, fg_color="#1e1e1e")
        self.main.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)
        self.main.grid_rowconfigure(0, weight=1)
        self.main.grid_columnconfigure(0, weight=1)
        
        # Pages
        self.pages = {}
        self.pages["Acceuil"] = Acceuil(self.main)
        self.pages["File d'attente"] = QueueView(self.main)
        self.pages["Favoris"] = FavoritesView(self.main)
        self.pages["Playlists"] = PlaylistsView(self.main)
        self.pages["Répertoire"] = DirectoriesView(self.main)
        self.pages["Paramètres"] = SettingsView(self.main)
        
        # Afficher la page d'accueil par défaut
        self.pages["Acceuil"].grid(row=0, column=0, sticky="nsew")
        self.current_page = "Acceuil"

        # Vue courante réellement affichée dans `self.main` : soit le nom
        # d'une page du sidebar (comme self.current_page), soit "lyrics"
        # quand la vue des paroles est superposée par-dessus. Nécessaire
        # car la vue des paroles n'appartient pas à la navigation du
        # sidebar (self.pages / self.current_page continuent de désigner
        # la page "de fond" sur laquelle on reviendra).
        self.current_view_name = self.current_page
        self.previous_view_name = None

        #############################
        # Vue des Paroles (superposée, ouverte depuis la pochette de la PlayerBar)
        #############################
        self.lyrics_page = LyricsView(self.main, app=self)

        #############################
        # Player
        #############################
        self.player = PlayerBar(self, app=self)
        self.player.grid(row=1, column=0, columnspan=2, sticky="ew", padx=5, pady=5)

    def show_lyrics_view(self, song=None):
        """Affiche la vue des paroles par-dessus la page actuellement
        visible. `song` est accepté pour compatibilité avec l'appelant
        (PlayerBar) mais la vue recharge de toute façon le morceau courant
        directement depuis le backend."""
        if self.current_view_name == "lyrics":
            return
        if self.current_page in self.pages:
            self.pages[self.current_page].grid_forget()
        self.previous_view_name = self.current_page
        self.lyrics_page.grid(row=0, column=0, sticky="nsew")
        if hasattr(self.lyrics_page, "refresh"):
            self.lyrics_page.refresh()
        self.current_view_name = "lyrics"

    def show_previous_view(self):
        """Masque la vue des paroles et restaure la page du sidebar qui
        était affichée avant son ouverture."""
        if self.current_view_name != "lyrics":
            return
        self.lyrics_page.grid_forget()
        target = self.previous_view_name or "Acceuil"
        if target in self.pages:
            self.pages[target].grid(row=0, column=0, sticky="nsew")
        self.current_page = target
        self.current_view_name = target
        self.previous_view_name = None

    
    def toogle_sidebar(self):
        """Toggle sidebar visibility"""
        if self.sidebar.state_open_sidebar:
            self.sidebar.reduce_sidebar()
        else:
            self.sidebar.open_sidebar()
    
    def changer_page(self, nom_page: str):
        """Change the current page/view"""
        # Mapping from sidebar text to page name
        page_mapping = {
            "acceuil": "Acceuil",
            "file d'attente": "File d'attente",
            "favoris": "Favoris",
            "playlists": "Playlists",
            "répertoire": "Répertoire",
            "paramètres": "Paramètres"
        }
        
        # Get the actual page name
        actual_page_name = page_mapping.get(nom_page.lower(), nom_page)
        
        # Hide current page (ou la vue des paroles si elle était ouverte
        # par-dessus une page au moment de la navigation via le sidebar)
        if self.current_view_name == "lyrics":
            self.lyrics_page.grid_forget()
        elif self.current_page in self.pages:
            self.pages[self.current_page].grid_forget()
        
        # Show selected page
        if actual_page_name in self.pages:
            page = self.pages[actual_page_name]
            page.grid(row=0, column=0, sticky="nsew")
            # Certaines pages (la file d'attente notamment) exposent une
            # méthode refresh() : elles ne se mettent pas à jour toutes
            # seules quand une action est faite depuis un autre onglet
            # (ex : ajouter un morceau à la file depuis Accueil), donc on
            # les recharge explicitement à chaque fois qu'on y navigue.
            if hasattr(page, "refresh"):
                page.refresh()
            self.current_page = actual_page_name
            self.current_view_name = actual_page_name
            self.previous_view_name = None
            
            # Update button colors
            for btn_name, btn in self.sidebar.boutons.items():
                btn.configure(fg_color=self.COLOR_BTN_DEFAULT)
            
            if actual_page_name in self.sidebar.boutons:
                self.sidebar.boutons[actual_page_name].configure(fg_color=self.COLOR_BTN_ACTIVE)