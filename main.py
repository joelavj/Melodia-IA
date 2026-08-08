"""
main.py — Version CustomTkinter
Assemble les composants du dossier view/ pour former l'interface Mélod'IA.
"""

import customtkinter as ctk

from views.Nav import NavBar
from views.Menu import SideMenu
from views.afficheList import ListDisplay
from views.LireChanson import PlayerBar
from views.BarreAffichier import LyricsPanel

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("green")


class MelodiaApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Mélod'IA — CustomTkinter")
        self.geometry("1200x750")
        self.minsize(900, 600)

        # Conteneur du haut : Nav
        self.nav = NavBar(self, on_toggle_menu=self.toggle_menu, on_search=self.on_search)
        self.nav.pack(side="top", fill="x")

        # Conteneur du milieu : Menu | Liste | Paroles
        body = ctk.CTkFrame(self, fg_color="#181818", corner_radius=0)
        body.pack(side="top", fill="both", expand=True)

        # 1. Création du menu latéral
        self.menu = SideMenu(
            body, 
            on_select=self.on_menu_select,
            on_import_success=self.on_import_success
        )
        self.menu.pack(side="left", fill="y")

        # 2. Création de l'affichage central des listes
        self.list_display = ListDisplay(body, on_item_click=self.on_item_click)
        self.list_display.pack(side="left", fill="both", expand=True)

        # Panneau des paroles
        self.lyrics_panel = LyricsPanel(body, on_rate=self.on_rate)
        self.lyrics_panel.pack(side="right", fill="y")

        # Conteneur du bas : lecteur
        self.player = PlayerBar(
            self,
            on_play_pause=self.on_play_pause,
            on_next=self.on_next,
            on_prev=self.on_prev,
            on_volume_change=self.on_volume_change,
        )
        self.player.pack(side="bottom", fill="x")

    # --- Callbacks ---
    def toggle_menu(self):
        self.menu.toggle()

    def on_search(self, query):
        print("Recherche :", query)

    def on_import_success(self, onglet):
        self.list_display.on_import_complete(onglet)

    def on_menu_select(self, label):
        print("Section sélectionnée :", label)
        self.list_display.changer_onglet(label)

    def on_item_click(self, category, item):
        print(f"{category} sélectionné :", item["titre"])
        # Met à jour la PlayerBar à partir de l'état du PlayerController
        self.player.update_status()

    def on_rate(self, note):
        print("Note attribuée :", note)

    def on_play_pause(self, is_playing):
        self.player.update_status()

    def on_next(self):
        self.player.update_status()

    def on_prev(self):
        self.player.update_status()

    def on_volume_change(self, value):
        print("Volume :", value)


if __name__ == "__main__":
    app = MelodiaApp()
    app.mainloop()