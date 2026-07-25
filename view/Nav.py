"""
Nav.py — CustomTkinter
Barre de navigation supérieure : bouton "3 lignes" (hamburger), logo Mélod'IA,
et barre de recherche.
"""

import customtkinter as ctk


class NavBar(ctk.CTkFrame):
    """Barre de navigation en haut de l'application."""

    def __init__(self, master, on_toggle_menu=None, on_search=None, **kwargs):
        super().__init__(master, height=64, corner_radius=0, fg_color="#121212", **kwargs)
        self.on_toggle_menu = on_toggle_menu
        self.on_search = on_search

        self.grid_columnconfigure(1, weight=1)
        self.pack_propagate(False)

        # --- Bouton hamburger (3 lignes) ---
        self.btn_menu = ctk.CTkButton(
            self,
            text="\u2630",  # caractère "3 lignes"
            width=40,
            height=40,
            font=ctk.CTkFont(size=20),
            fg_color="transparent",
            hover_color="#282828",
            command=self._toggle_menu,
        )
        self.btn_menu.grid(row=0, column=0, padx=(12, 8), pady=10)

        # --- Logo Mélod'IA ---
        self.lbl_logo = ctk.CTkLabel(
            self,
            text="Mélod'IA",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color="#1DB954",
        )
        self.lbl_logo.grid(row=0, column=1, sticky="w", padx=(0, 20))

        # --- Barre de recherche ---
        self.search_frame = ctk.CTkFrame(self, fg_color="#242424", corner_radius=20, height=36)
        self.search_frame.grid(row=0, column=2, sticky="e", padx=16, pady=12)

        self.entry_search = ctk.CTkEntry(
            self.search_frame,
            placeholder_text="Rechercher un titre, un artiste, un album...",
            width=320,
            height=32,
            border_width=0,
            fg_color="transparent",
        )
        self.entry_search.pack(side="left", padx=(12, 4), pady=2)
        self.entry_search.bind("<Return>", self._trigger_search)

        self.btn_search = ctk.CTkButton(
            self.search_frame,
            text="\U0001F50D",
            width=28,
            height=28,
            corner_radius=14,
            fg_color="transparent",
            hover_color="#333333",
            command=self._trigger_search,
        )
        self.btn_search.pack(side="left", padx=(0, 8))

    def _toggle_menu(self):
        if self.on_toggle_menu:
            self.on_toggle_menu()

    def _trigger_search(self, event=None):
        query = self.entry_search.get().strip()
        if self.on_search and query:
            self.on_search(query)


if __name__ == "__main__":
    app = ctk.CTk()
    app.geometry("900x120")
    nav = NavBar(app, on_toggle_menu=lambda: print("toggle menu"),
                 on_search=lambda q: print("recherche:", q))
    nav.pack(fill="x")
    app.mainloop()
