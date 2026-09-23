import customtkinter as ctk
from utils.function import load_image
from utils.constante import BASE_DIR


class Sidebar(ctk.CTkFrame):
    def __init__(self, master, toogle_sidebar, changer_page):
        self.width_sidebar = 200
        super().__init__(
            master,
            fg_color="#2c3e50",
            width=self.width_sidebar,
            corner_radius=0
        )
        self.pack_propagate(False)
        
        self.state_open_sidebar = True
        self.changer_page = changer_page
        
        # ===== HEADER =====
        nav_frame = ctk.CTkFrame(self, fg_color="#34495e", height=50, corner_radius=0)
        nav_frame.pack(side="top", fill="x")
        nav_frame.pack_propagate(False)
        
        self.title_label = ctk.CTkLabel(
            nav_frame,
            text="NAVIGATION",
            text_color="white",
            font=("Arial", 10, "bold")
        )
        self.title_label.pack(side="left", padx=10, pady=10)
        
        toggle_btn = ctk.CTkButton(
            nav_frame,
            text="☰",
            command=toogle_sidebar,
            width=40,
            height=40,
            fg_color="#2c3e50",
            text_color="white",
            font=("Arial", 18)
        )
        toggle_btn.pack(side="right", padx=10, pady=5)
        
        # ===== LOGO/INFO =====
        self.info_frame = ctk.CTkFrame(self, fg_color="#2c3e50")
        self.info_frame.pack(side="top", fill="x", padx=10, pady=10)
        
        self.logo_label = ctk.CTkLabel(
            self.info_frame,
            text="🎵 Melod'IA",
            text_color="white",
            font=("Arial", 12, "bold")
        )
        self.logo_label.pack(fill="x", pady=5)
        
        # ===== NAVIGATION BUTTONS =====
        self.boutons = {}
        
        nav_items = [
            ("🏠 Acceuil", "acceuil"),
            ("⏯️ File d'attente", "file d'attente"),
            ("❤️ Favoris", "favoris"),
            ("📋 Playlists", "playlists"),
            ("📁 Répertoire", "répertoire"),
            ("⚙️ Paramètres", "paramètres")
        ]
        
        # display_text complet ("🏠 Acceuil") pour le mode étendu, icône
        # seule (premier "mot", avant l'espace) pour le mode réduit.
        self._full_texts = {}
        self._icon_texts = {}

        for display_text, command_text in nav_items:
            btn = ctk.CTkButton(
                self,
                text=display_text,
                command=lambda c=command_text: changer_page(c),
                fg_color="#34495e",
                hover_color="#1abc9c",
                text_color="white",
                font=("Arial", 11),
                anchor="w",
                height=40,
                corner_radius=5
            )
            btn.pack(side="top", fill="x", padx=5, pady=3)
            
            # Store button by the key name
            btn_key = command_text.capitalize()
            if "d'attente" in command_text:
                btn_key = "File d'attente"
            
            self.boutons[btn_key] = btn
            self._full_texts[btn_key] = display_text
            self._icon_texts[btn_key] = display_text.split(" ", 1)[0]
    
    def open_sidebar(self):
        """Open the sidebar : ré-affiche le texte complet des boutons et
        de l'en-tête, en plus d'élargir le cadre."""
        self.width_sidebar = 200
        self.configure(width=self.width_sidebar)
        self.title_label.pack(side="left", padx=10, pady=10)
        self.info_frame.pack(side="top", fill="x", padx=10, pady=10)
        for btn_key, btn in self.boutons.items():
            btn.configure(text=self._full_texts[btn_key], anchor="w")
        self.state_open_sidebar = True
    
    def reduce_sidebar(self):
        """Reduce the sidebar : bascule en mode icônes seules (le texte
        complet des boutons et le titre "NAVIGATION" débordaient et se
        chevauchaient sur les 60px du cadre réduit)."""
        self.width_sidebar = 60
        self.configure(width=self.width_sidebar)
        self.title_label.pack_forget()
        self.info_frame.pack_forget()
        for btn_key, btn in self.boutons.items():
            btn.configure(text=self._icon_texts[btn_key], anchor="center")
        self.state_open_sidebar = False
