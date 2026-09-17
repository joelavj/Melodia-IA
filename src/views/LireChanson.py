"""
LireChanson.py — CustomTkinter
Barre de lecture en bas de l'application : pochette, titre/artiste, contrôles
(stop, précédent, play/pause, suivant, répéter), volume et barre de progression.
"""
import sys
import os
import time

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
        self.duree_totale = 0  # En secondes
        self.temps_actuel = 0  # En secondes
        self._is_user_seeking = False  # Évite les conflits pendant le glissement

        self._cover_label = None
        self.pack_propagate(False)
        self.grid_columnconfigure(1, weight=1)

        # --- Pochette + titre (gauche) ---
        left = ctk.CTkFrame(self, fg_color="transparent")
        left.grid(row=0, column=0, sticky="w", padx=16, pady=10)

        self.cover = ctk.CTkButton(left, text="", fg_color="#1DB954", width=56, height=56, corner_radius=6, command=self.afficher)
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

        # 1. Bouton Stop
        self.btn_stop = ctk.CTkButton(
            controls, text="\u23F9", width=36, height=36,
            fg_color="transparent", hover_color="#282828",
            font=ctk.CTkFont(size=16), command=self._stop
        )
        self.btn_stop.pack(side="left", padx=4)

        # 2. Bouton Précédent
        self.btn_prev = ctk.CTkButton(
            controls, text="\u23EE", width=36, height=36,
            fg_color="transparent", hover_color="#282828",
            font=ctk.CTkFont(size=16), command=self._prev
        )
        self.btn_prev.pack(side="left", padx=4)

        # 3. Bouton Play/Pause
        self.btn_play = ctk.CTkButton(
            controls, text="\u25B6", width=42, height=42,
            corner_radius=21, fg_color="#1DB954",
            hover_color="#17a34a", text_color="#000000",
            font=ctk.CTkFont(size=16), command=self._play_pause
        )
        self.btn_play.pack(side="left", padx=6)

        # 4. Bouton Suivant
        self.btn_next = ctk.CTkButton(
            controls, text="\u23ED", width=36, height=36,
            fg_color="transparent", hover_color="#282828",
            font=ctk.CTkFont(size=16), command=self._next
        )
        self.btn_next.pack(side="left", padx=4)

        # 5. Bouton Répéter
        self.btn_repeat = ctk.CTkButton(
            controls, text="\U000027A1", width=36, height=36,
            fg_color="transparent", hover_color="#282828",
            font=ctk.CTkFont(size=16), command=self._change_repeat
        )
        self.btn_repeat.pack(side="left", padx=4)

        # Conteneur pour le temps et la barre de progression
        progress_frame = ctk.CTkFrame(center, fg_color="transparent")
        progress_frame.pack(fill="x", padx=20, pady=(6, 0))

        # Temps écoulé
        self.lbl_temps_actuel = ctk.CTkLabel(progress_frame, text="00:00", font=ctk.CTkFont(size=11), text_color="#a0a0a0")
        self.lbl_temps_actuel.pack(side="left", padx=(0, 8))

        # Barre de progression colorée en VERT (#1DB954)
        self.progress = ctk.CTkSlider(
            progress_frame,
            from_=0,
            to=100,
            command=self._on_seek_drag,
            progress_color="#1DB954",
            button_color="#1DB954",
            button_hover_color="#17a34a",
            fg_color="#404040"
        )
        self.progress.set(0)
        self.progress.pack(side="left", fill="x", expand=True)

        # Temps de fin (durée totale)
        self.lbl_temps_total = ctk.CTkLabel(progress_frame, text="00:00", font=ctk.CTkFont(size=11), text_color="#a0a0a0")
        self.lbl_temps_total.pack(side="right", padx=(8, 0))

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

        # Démarrage des boucles de rafraîchissement
        self._process_event()
        self._rafraichir_temps()

    def _process_event(self):
        """Vérifie rapidement (10x par seconde) la fin de chanson pour enchaîner la suivante."""
        try:
            pc.process_event()
            self.update_status()
        except Exception as e:
            print(f"[PlayerBar] Erreur process_event: {e}")
        self.after(100, self._process_event)

    def formater_temps(self, secondes: float) -> str:
        """Convertit un temps en secondes vers le format MM:SS."""
        if secondes is None or secondes < 0:
            secondes = 0
        return time.strftime('%M:%S', time.gmtime(secondes))

    def afficher(self):
        logo_ispm_path = "asset/ispm-logo.png"
        logo_size = (40, 40)
        if os.path.exists(logo_ispm_path):
            img_ispm_pil = Image.open(logo_ispm_path)
            self.photo_ispm = ctk.CTkImage(
                light_image=img_ispm_pil,
                dark_image=img_ispm_pil,
                size=logo_size
            )
            if hasattr(self, "brand_container"):
                self.logo_ispm_label = ctk.CTkLabel(
                    self.brand_container,
                    image=self.photo_ispm,
                    text="",
                    fg_color="transparent"
                )
                self.logo_ispm_label.pack(side="right", padx=5)

    def update_status(self):
        """Récupère l'état actuel depuis le PlayerController et met à jour l'UI."""
        try:
            status = pc.player_status()
            song = status.get("song")
            state = str(status.get("state", "")).upper()
            repeat_mode = status.get("repeat")

            if song:
                titre = getattr(song, 'title', None) or getattr(song, 'name', None) or os.path.basename(getattr(song, 'path', '')) or "Titre inconnu"
                artiste = getattr(song, 'artist', None) or getattr(song, 'artist_name', 'Artiste inconnu')
                
                self.duree_totale = getattr(song, 'duration', 0) or getattr(song, 'duree', 0) or 0
                self.lbl_temps_total.configure(text=self.formater_temps(self.duree_totale))

                self.set_song(titre, artiste)

            # 1. Gestion de l'icône Play/Pause
            is_playing = "PLAYING" in state or ("PLAY" in state and "PAUSE" not in state and "STOP" not in state)
            self.is_playing = is_playing
            self.btn_play.configure(text="\u23F8" if is_playing else "\u25B6")

            # 2. Mise à jour de l'icône Répéter
            str_mode = str(repeat_mode).upper()
            if "ONE" in str_mode or "SINGLE" in str_mode or repeat_mode == 2:
                self.btn_repeat.configure(text="\U0001F502", text_color="#F8FCFA")
            elif "ALL" in str_mode or repeat_mode == 1:
                self.btn_repeat.configure(text="\U0001F501", text_color="#F1F1F1")
            else:
                self.btn_repeat.configure(text="\U000027A1", text_color="#FFFFFF")

        except Exception as e:
            print(f"[PlayerBar] Erreur update_status: {e}")

    def _rafraichir_temps(self):
        """Met à jour le temps de lecture chaque seconde."""
        if self.is_playing and not self._is_user_seeking:
            try:
                self.temps_actuel += 1

                if self.duree_totale > 0:
                    progression = (self.temps_actuel / self.duree_totale) * 100
                    self.progress.set(min(progression, 100))
                
                self.lbl_temps_actuel.configure(text=self.formater_temps(self.temps_actuel))
            except Exception:
                pass

        self.after(1000, self._rafraichir_temps)

    def _on_seek_drag(self, valeur):
        """Gère le déplacement manuel du curseur de recherche (Seek)."""
        if self.duree_totale > 0 and self.is_playing:
            self._is_user_seeking = True
            nouvelle_pos = int((valeur / 100) * self.duree_totale)
            self.temps_actuel = nouvelle_pos
            self.lbl_temps_actuel.configure(text=self.formater_temps(nouvelle_pos))

            pc.seek(nouvelle_pos)
            if self.on_seek:
                self.on_seek(nouvelle_pos)

            self._is_user_seeking = False

    def _play_pause(self):
        pc.play_song()
        self.update_status()
        if self.on_play_pause:
            self.on_play_pause(self.is_playing)

    def _stop(self):
        """Arrête la lecture, réinitialise le compteur et bloque le défilement."""
        pc.stop_play()
        self.is_playing = False
        self.temps_actuel = 0
        self.progress.set(0)
        self.lbl_temps_actuel.configure(text="00:00")
        self.btn_play.configure(text="\u25B6")

    def _change_repeat(self):
        pc.change_repeat_mode()
        self.update_status()

    def _next(self):
        self.temps_actuel = 0
        self.progress.set(0)
        pc.next_song()
        self.update_status()
        if self.on_next:
            self.on_next()

    def _prev(self):
        self.temps_actuel = 0
        self.progress.set(0)
        pc.previous_song()
        self.update_status()
        if self.on_prev:
            self.on_prev()

    def set_song(self, titre, artiste, cover_path=None):
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
        pc.change_volume(int(valeur))

        if hasattr(self, "on_volume_change") and self.on_volume_change:
            self.on_volume_change(valeur)