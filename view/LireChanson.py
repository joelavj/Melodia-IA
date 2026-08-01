"""
LireChanson.py — CustomTkinter
Barre de lecture en bas de l'application : pochette, titre/artiste, contrôles
(précédent, play/pause, suivant), volume et barre de progression.
"""

from turtle import right

import customtkinter as ctk


class PlayerBar(ctk.CTkFrame):
    """Barre de lecture du morceau en cours."""

    def __init__(self, master, on_play_pause=None, on_next=None, on_prev=None,
                 on_volume_change=None, on_seek=None, **kwargs):
        super().__init__(master, height=90, corner_radius=0, fg_color="#181818", **kwargs)
        self.on_play_pause = on_play_pause
        self.on_next = on_next
        self.on_prev = on_prev
        self.on_volume_change = on_volume_change
        self.on_seek = on_seek

        self.is_playing = False
        self.pack_propagate(False)
        self.grid_columnconfigure(1, weight=1)

        # --- Pochette + titre (gauche) ---
        left = ctk.CTkFrame(self, fg_color="transparent")
        left.grid(row=0, column=0, sticky="w", padx=16, pady=10)

        self.cover = ctk.CTkFrame(left, fg_color="#1DB954", width=56, height=56, corner_radius=6)
        self.cover.pack(side="left")
        self.cover.pack_propagate(False)

        info = ctk.CTkFrame(left, fg_color="transparent")
        info.pack(side="left", padx=10)
        self.lbl_titre = ctk.CTkLabel(info, text="Aucun morceau", font=ctk.CTkFont(size=13, weight="bold"))
        self.lbl_titre.pack(anchor="w")
        self.lbl_artiste = ctk.CTkLabel(info, text="—", font=ctk.CTkFont(size=11), text_color="#a0a0a0")
        self.lbl_artiste.pack(anchor="w")

        # --- Contrôles + barre de progression (centre) ---
        center = ctk.CTkFrame(self, fg_color="transparent")
        center.grid(row=0, column=1, sticky="ew", pady=10)
        center.grid_columnconfigure(0, weight=1)

        controls = ctk.CTkFrame(center, fg_color="transparent")
        controls.pack()

        self.btn_prev = ctk.CTkButton(controls, text="\u23EE", width=36, height=36,
                                       fg_color="transparent", hover_color="#282828",
                                       font=ctk.CTkFont(size=16), command=self._prev)
        self.btn_prev.pack(side="left", padx=6)

        self.btn_play = ctk.CTkButton(controls, text="\u25B6", width=42, height=42,
                                       corner_radius=21, fg_color="#1DB954",
                                       hover_color="#17a34a", text_color="#000000",
                                       font=ctk.CTkFont(size=16), command=self._play_pause)
        self.btn_play.pack(side="left", padx=6)

        self.btn_next = ctk.CTkButton(controls, text="\u23ED", width=36, height=36,
                                       fg_color="transparent", hover_color="#282828",
                                       font=ctk.CTkFont(size=16), command=self._next)
        self.btn_next.pack(side="left", padx=6)

        self.progress = ctk.CTkSlider(center, from_=0, to=100, command=self._seek)
        self.progress.set(0)
        self.progress.pack(fill="x", padx=40, pady=(8, 0))

        # --- Volume (droite) ---
        right = ctk.CTkFrame(self, fg_color="transparent")
        right.grid(row=0, column=2, sticky="e", padx=16)

        # 1. Interface utilisateur (UI)
        self.lbl_volume = ctk.CTkLabel(right, text="\U0001F50A", font=ctk.CTkFont(size=14))
        self.lbl_volume.pack(side="left", padx=(0, 6))

        # On pointe directement 'command' vers mettre_a_jour_volume
        self.volume = ctk.CTkSlider(
        right, from_=0, to=100, width=100, command=self.mettre_a_jour_volume)
        self.volume.set(70)
        self.volume.pack(side="left")

    # --- callbacks internes ---
    def _play_pause(self):
        self.is_playing = not self.is_playing
        self.btn_play.configure(text="\u23F8" if self.is_playing else "\u25B6")
        if self.on_play_pause:
            self.on_play_pause(self.is_playing)

    def _next(self):
        if self.on_next:
            self.on_next()

    def _prev(self):
        if self.on_prev:
            self.on_prev()

    def _volume_change(self, value):
        if self.on_volume_change:
            self.on_volume_change(value)

    def _seek(self, value):
        if self.on_seek:
            self.on_seek(value)

    # --- API publique ---
    def set_song(self, titre, artiste):
        self.lbl_titre.configure(text=titre)
        self.lbl_artiste.configure(text=artiste)
    
# 2. Méthodes
    def obtenir_icone_volume(self, niveau: float) -> str:
        # niveau est compris entre 0 et 100
        if niveau == 0:
            return "\U0001F507"  # Silence / Nul 🔇
        elif niveau < 33:
            return "\U0001F508"  # Bas 🔈
        elif niveau < 66:
            return "\U0001F509"  # Moyen (~50%) 🔉
        else:
            return "\U0001F50A"  # Plein 🔊


    def mettre_a_jour_volume(self, valeur: float):
        # Met à jour l'icône du label selon la valeur actuelle du slider (0 à 100)
        nouvelle_icone = self.obtenir_icone_volume(valeur)
        self.lbl_volume.configure(text=nouvelle_icone)

        # Appelle le callback externe si défini
        if hasattr(self, "on_volume_change") and self.on_volume_change:
            self.on_volume_change(valeur)

if __name__ == "__main__":
    app = ctk.CTk()
    app.geometry("900x100")
    player = PlayerBar(app)
    player.pack(fill="x")
    player.set_song("Miverina", "Ny Ainga")
    app.mainloop()
