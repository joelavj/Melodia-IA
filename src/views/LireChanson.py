"""
LireChanson.py — CustomTkinter
Barre de lecture en bas de l'application : pochette, titre/artiste, contrôles
(précédent, play/pause, suivant), volume et barre de progression.
"""
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from controllers.player_controller import player_controller as pc
import customtkinter as ctk
from PIL import Image


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
        self._cover_label = None
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

        self.lbl_volume = ctk.CTkLabel(right, text="\U0001F50A", font=ctk.CTkFont(size=14))
        self.lbl_volume.pack(side="left", padx=(0, 6))

        self.volume = ctk.CTkSlider(
            right, from_=0, to=100, width=100, command=self.mettre_a_jour_volume
        )
        self.volume.set(70)
        self.volume.pack(side="left")

    # --- Synchronisation avec le PlayerController ---
    def update_status(self):
        """Récupère l'état actuel depuis le PlayerController et met à jour l'UI."""
        try:
            status = pc.player_status()
            song = status.get("song")
            state = str(status.get("state", ""))

            if song:
                titre = getattr(song, 'title', None) or getattr(song, 'name', None) or os.path.basename(getattr(song, 'path', '')) or "Titre inconnu"
                artiste = getattr(song, 'artist', None) or getattr(song, 'artist_name', 'Artiste inconnu')
                self.set_song(titre, artiste)

            # Basculer l'icône entre Play (▶) et Pause (⏸)
            is_playing = "PLAY" in state.upper() or "PLAYING" in state.upper()
            self.btn_play.configure(text="\u23F8" if is_playing else "\u25B6")
        except Exception as e:
            print(f"[PlayerBar] Erreur update_status: {e}")

    def _play_pause(self):
        pc.play_song()
        self.update_status()
        if self.on_play_pause:
            self.on_play_pause(self.is_playing)

    def _next(self):
        pc.next_song()
        self.update_status()
        if self.on_next:
            self.on_next()

    def _prev(self):
        pc.previous_song()
        self.update_status()
        if self.on_prev:
            self.on_prev()

    def _volume_change(self, value):
        if self.on_volume_change:
            self.on_volume_change(value)

    def _seek(self, value):
        if self.on_seek:
            self.on_seek(value)

    def set_song(self, titre, artiste, cover_path=None):
        """Met à jour le titre, l'artiste et la pochette du morceau affiché."""
        self.lbl_titre.configure(text=titre)
        self.lbl_artiste.configure(text=artiste)
        self._set_cover(cover_path)

    def _set_cover(self, cover_path):
        if cover_path and os.path.exists(cover_path):
            try:
                img = Image.open(cover_path)
                ctk_img = ctk.CTkImage(light_image=img, dark_image=img, size=(56, 56))
                if self._cover_label is None:
                    self._cover_label = ctk.CTkLabel(self.cover, text="", image=ctk_img)
                    self._cover_label.place(relx=0.5, rely=0.5, anchor="center")
                else:
                    self._cover_label.configure(image=ctk_img)
                self._cover_label.image = ctk_img
                return
            except Exception as e:
                print(f"[LireChanson] Erreur chargement pochette: {e}")

        if self._cover_label is not None:
            self._cover_label.destroy()
            self._cover_label = None

    def obtenir_icone_volume(self, niveau: float) -> str:
        if niveau == 0:
            return "\U0001F507"
        elif niveau < 33:
            return "\U0001F508"
        elif niveau < 66:
            return "\U0001F509"
        else:
            return "\U0001F50A"

    def mettre_a_jour_volume(self, valeur: float):
        nouvelle_icone = self.obtenir_icone_volume(valeur)
        self.lbl_volume.configure(text=nouvelle_icone)

        if hasattr(self, "on_volume_change") and self.on_volume_change:
            self.on_volume_change(valeur)