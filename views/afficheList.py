"""
afficheList.py — CustomTkinter
Affichage des listes : albums, artistes, morceaux et playlists sous forme de cartes,
organisées par onglets.
"""

import customtkinter as ctk

# Données factices (à remplacer par les données réelles issues de la BDD)
DUMMY_DATA = {
    "Albums": [
        {"titre": "Nocturne", "sous_titre": "Ambiance • 2024"},
        {"titre": "Horizon", "sous_titre": "Pop • 2023"},
        {"titre": "Racines", "sous_titre": "Salegy • 2022"},
    ],
    "Artistes": [
        {"titre": "Ny Ainga", "sous_titre": "12 morceaux"},
        {"titre": "Voary", "sous_titre": "8 morceaux"},
        {"titre": "Tsiky Band", "sous_titre": "20 morceaux"},
    ],
    "Morceaux": [
        {"titre": "Miverina", "sous_titre": "Ny Ainga • 3:42"},
        {"titre": "Tsara Ihany", "sous_titre": "Voary • 4:01"},
        {"titre": "Fitiavana", "sous_titre": "Tsiky Band • 3:15"},
    ],
    "Playlists": [
        {"titre": "Mes favoris", "sous_titre": "24 titres"},
        {"titre": "Détente", "sous_titre": "15 titres"},
        {"titre": "Route Antananarivo", "sous_titre": "30 titres"},
    ],
}


class ListDisplay(ctk.CTkFrame):
    """Zone centrale : onglets Albums / Artistes / Morceaux / Playlists."""

    def __init__(self, master, on_item_click=None, **kwargs):
        super().__init__(master, fg_color="#181818", corner_radius=0, **kwargs)
        self.on_item_click = on_item_click

        self.tabview = ctk.CTkTabview(
            self,
            fg_color="#181818",
            segmented_button_fg_color="#242424",
            segmented_button_selected_color="#1DB954",
            segmented_button_selected_hover_color="#17a34a",
        )
        self.tabview.pack(fill="both", expand=True, padx=16, pady=16)

        for tab_name in DUMMY_DATA.keys():
            self.tabview.add(tab_name)
            self._build_tab(self.tabview.tab(tab_name), tab_name)

    def _build_tab(self, tab, tab_name):
        scroll = ctk.CTkScrollableFrame(tab, fg_color="transparent")
        scroll.pack(fill="both", expand=True)

        n_cols = 4
        for i in range(n_cols):
            scroll.grid_columnconfigure(i, weight=1)

        items = DUMMY_DATA[tab_name]
        for index, item in enumerate(items):
            row, col = divmod(index, n_cols)
            self._build_card(scroll, item, tab_name).grid(
                row=row, column=col, padx=8, pady=8, sticky="nsew"
            )

    def _build_card(self, parent, item, category):
        card = ctk.CTkFrame(parent, fg_color="#242424", corner_radius=10, width=160, height=200)
        card.grid_propagate(False)

        cover = ctk.CTkFrame(card, fg_color="#1DB954", corner_radius=8, width=140, height=120)
        cover.pack(padx=10, pady=(10, 6))
        cover.pack_propagate(False)

        lbl_titre = ctk.CTkLabel(card, text=item["titre"], font=ctk.CTkFont(size=13, weight="bold"))
        lbl_titre.pack(padx=10, anchor="w")

        lbl_sous = ctk.CTkLabel(card, text=item["sous_titre"], font=ctk.CTkFont(size=11),
                                 text_color="#a0a0a0")
        lbl_sous.pack(padx=10, anchor="w")

        card.bind("<Button-1>", lambda e: self._click(category, item))
        for child in card.winfo_children():
            child.bind("<Button-1>", lambda e: self._click(category, item))

        return card

    def _click(self, category, item):
        if self.on_item_click:
            self.on_item_click(category, item)


if __name__ == "__main__":
    app = ctk.CTk()
    app.geometry("800x600")
    lst = ListDisplay(app, on_item_click=lambda cat, it: print(cat, it))
    lst.pack(fill="both", expand=True)
    app.mainloop()
