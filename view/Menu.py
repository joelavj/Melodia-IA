"""
Menu.py — CustomTkinter
Menu latéral (sidebar) rétractable.
"""
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import customtkinter as ctk
import repositories.artist_repository as artist_repo

MENU_ITEMS = [
    ("\U0001F3E0", "Accueil"),
    ("\U0001F4BF", "Albums"),
    ("\U0001F3A4", "Artistes"),
    ("\U0001F3B5", "Morceaux"),
    ("\U0001F4CB", "Playlists"),
    ("\u2764", "Favoris"),
    ("\u2699", "Paramètres"),
]


class SideMenu(ctk.CTkFrame):
    """Menu latéral avec navigation entre les sections de l'application."""

    def __init__(self, master, on_select=None, width_expanded=220, width_collapsed=0, **kwargs):
        super().__init__(master, width=width_expanded, corner_radius=0, fg_color="#0d0d0d", **kwargs)
        self.on_select = on_select
        self.width_expanded = width_expanded
        self.width_collapsed = width_collapsed
        self.is_open = True
        self.buttons = {}

        self.pack_propagate(False)
        self._build_items()

    def _build_items(self):
        for icon, label in MENU_ITEMS:
            btn = ctk.CTkButton(
                self,
                text=f"  {icon}   {label}",
                anchor="w",
                fg_color="transparent",
                hover_color="#1f1f1f",
                text_color="#e0e0e0",
                font=ctk.CTkFont(size=14),
                height=40,
                command=lambda l=label: self._select(l),
            )
            btn.pack(fill="x", padx=8, pady=2)
            self.buttons[label] = btn

    def _select(self, label):
        # Mise à jour visuelle du bouton actif
        for name, btn in self.buttons.items():
            btn.configure(
                fg_color="#1DB954" if name == label else "transparent",
                text_color="#000000" if name == label else "#e0e0e0"
            )
        
        # Envoi de la section sélectionnée au contrôleur/app principal
        if self.on_select:
            self.on_select(label)

    def toggle(self):
        """Ouvre ou ferme le menu."""
        if self.is_open:
            self.configure(width=self.width_collapsed)
            self.pack_forget()
        else:
            self.configure(width=self.width_expanded)
            self.pack(side="left", fill="y")
        self.is_open = not self.is_open