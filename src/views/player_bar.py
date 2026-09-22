"""
Melodia-IA - Barre de pilote de lecture (PlayerBar)
Architecture MVC - Vue du lecteur audio située en bas de l'application.

Fonctionnalités :
- Pochette à gauche : clic -> bascule vers la vue Paroles (Lyrics) dans la frame main, re-clic -> retour.
- Ligne 1 : Titre morceau - Nom artiste / Titre album
- Ligne 2 : Temps actuel - Barre de progression horizontale interactive (seek) - Durée totale
- Ligne 3 : Pilotes de lecture :
    * Retirer de la file d'attente (cross.png)
    * Favori dynamique (favori.png / not-favori.png)
    * Précédent (rewind.png)
    * Play / Pause dynamique (play.png / pause.png)
    * Stop (stop.png)
    * Suivant (forward.png)
    * Répétition cyclique (no-repeat.png -> repeat-all.png -> repeat-one.png)
    * Contrôle de volume horizontal avec icône (volume-down.png / volume-mute.png)
"""

import os
import math
from PIL import Image, ImageTk

try:
    import customtkinter as ctk
    BASE_FRAME = ctk.CTkFrame
    USE_CTK = True
except ImportError:
    import tkinter as ctk
    BASE_FRAME = ctk.Frame
    USE_CTK = False


class PlayerBar(BASE_FRAME):
    def __init__(self, parent, app=None, player_controller=None, queue_controller=None,
                 favori_controller=None, lyrics_controller=None, **kwargs):
        super().__init__(parent, **kwargs)
        self.app = app
        self.player_controller = player_controller
        self.queue_controller = queue_controller
        self.favori_controller = favori_controller
        self.lyrics_controller = lyrics_controller

        # État interne
        self.is_playing = False
        self.is_seeking = False
        self.current_song = None
        self.current_duration = 0.0
        self.current_position = 0.0
        self.is_muted = False
        self.previous_volume = 70
        self.repeat_mode = "none"  # "none", "all", "one"
        self.is_in_lyrics_view = False

        # Répertoire des icônes assets
        self.assets_dir = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "..", "assets")
        )

        # Cache des icônes
        self.icons = {}
        self._load_all_icons()

        # Construction de l'interface
        self._setup_ui()

        # Démarrage de la boucle de synchronisation temporelle
        self._start_playback_poller()

    def _load_icon(self, filename, size=(24, 24)):
        """Charge une icône depuis le dossier assets de manière sûre."""
        path = os.path.join(self.assets_dir, filename)
        if not os.path.exists(path):
            alt_path = os.path.join(os.path.dirname(__file__), "assets", filename)
            if os.path.exists(alt_path):
                path = alt_path
            else:
                return None
        try:
            pil_img = Image.open(path)
            if USE_CTK:
                return ctk.CTkImage(light_image=pil_img, dark_image=pil_img, size=size)
            else:
                resized = pil_img.resize(size, Image.Resampling.LANCZOS)
                return ImageTk.PhotoImage(resized)
        except Exception as e:
            print(f"[PlayerBar] Erreur chargement icône {filename}: {e}")
            return None

    def _load_all_icons(self):
        """Charge toutes les icônes nécessaires à la barre de lecture."""
        icon_files = {
            "play": ("play.png", (28, 28)),
            "pause": ("pause.png", (28, 28)),
            "stop": ("stop.png", (20, 20)),
            "rewind": ("rewind.png", (22, 22)),
            "forward": ("forward.png", (22, 22)),
            "favori": ("favori.png", (22, 22)),
            "not_favori": ("not-favori.png", (22, 22)),
            "cross": ("cross.png", (18, 18)),
            "no_repeat": ("no-repeat.png", (20, 20)),
            "repeat_all": ("repeat-all.png", (20, 20)),
            "repeat_one": ("repeat-one.png", (20, 20)),
            "volume_down": ("volume-down.png", (20, 20)),
            "volume_mute": ("volume-mute.png", (20, 20)),
            "default_cover": ("melodia_ia.png", (64, 64)),
        }
        for key, (fname, sz) in icon_files.items():
            self.icons[key] = self._load_icon(fname, sz)

    def _setup_ui(self):
        """Construit l'arborescence visuelle de la barre."""
        if USE_CTK:
            self.configure(fg_color=("gray92", "#1E1E24"), height=100, corner_radius=0)
        self.pack_propagate(False)

        # 1. ZONE GAUCHE : Pochette cliquable (Album Cover)
        self.cover_frame = ctk.CTkFrame(self, fg_color="transparent", width=80, height=80)
        self.cover_frame.pack(side="left", padx=(15, 12), pady=8)
        self.cover_frame.pack_propagate(False)

        self.btn_cover = ctk.CTkButton(
            self.cover_frame,
            text="",
            image=self.icons.get("default_cover"),
            width=68,
            height=68,
            corner_radius=8,
            fg_color=("gray85", "#2A2A32"),
            hover_color=("gray75", "#3D3D48"),
            command=self.toggle_lyrics_display
        )
        self.btn_cover.pack(fill="both", expand=True)

        # 2. ZONE CENTRALE / DROITE : Structure à 3 lignes
        self.content_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.content_frame.pack(side="left", fill="both", expand=True, padx=(0, 20), pady=6)

        # LIGNE 1 : 'titre morceau - nom artiste / titre album'
        self.row1_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        self.row1_frame.pack(fill="x", pady=(2, 2))

        self.lbl_track_info = ctk.CTkLabel(
            self.row1_frame,
            text="Aucun morceau en cours - Melodia-IA",
            font=ctk.CTkFont(family="Arial", size=13, weight="bold"),
            anchor="w",
            text_color=("gray20", "#EAEAEA")
        )
        self.lbl_track_info.pack(side="left", fill="x", expand=True)

        # LIGNE 2 : Durée actuelle | Barre de progression | Durée totale
        self.row2_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        self.row2_frame.pack(fill="x", pady=(2, 4))

        self.lbl_curr_time = ctk.CTkLabel(
            self.row2_frame,
            text="00:00",
            width=45,
            font=ctk.CTkFont(family="Arial", size=11),
            text_color=("gray40", "#A0A0A0")
        )
        self.lbl_curr_time.pack(side="left", padx=(0, 8))

        self.progress_slider = ctk.CTkSlider(
            self.row2_frame,
            from_=0,
            to=100,
            height=14,
            corner_radius=7,
            progress_color=("#1f538d", "#1DB954"),
            button_color=("#1f538d", "#1DB954"),
            button_hover_color=("#14375e", "#1ed760"),
            button_length=12,
            command=self._on_seek_drag
        )
        self.progress_slider.set(0)
        self.progress_slider.pack(side="left", fill="x", expand=True)
        self.progress_slider.bind("<ButtonRelease-1>", self._on_seek_release)

        self.lbl_total_time = ctk.CTkLabel(
            self.row2_frame,
            text="00:00",
            width=45,
            font=ctk.CTkFont(family="Arial", size=11),
            text_color=("gray40", "#A0A0A0")
        )
        self.lbl_total_time.pack(side="left", padx=(8, 0))

        # LIGNE 3 : Pilotes de lecture & Volume horizontal
        self.row3_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        self.row3_frame.pack(fill="x", pady=(0, 2))

        # Section contrôles média
        self.media_controls_frame = ctk.CTkFrame(self.row3_frame, fg_color="transparent")
        self.media_controls_frame.pack(side="left")

        # Retirer de la file (cross.png)
        self.btn_remove_queue = self._create_icon_btn(
            self.media_controls_frame, "cross", self.on_remove_from_queue, width=32, height=32
        )
        self.btn_remove_queue.pack(side="left", padx=4)

        # Favori (favori.png / not-favori.png)
        self.btn_favori = self._create_icon_btn(
            self.media_controls_frame, "not_favori", self.on_toggle_favori, width=32, height=32
        )
        self.btn_favori.pack(side="left", padx=4)

        # Précédent (rewind.png)
        self.btn_prev = self._create_icon_btn(
            self.media_controls_frame, "rewind", self.on_previous, width=32, height=32
        )
        self.btn_prev.pack(side="left", padx=6)

        # Play / Pause (play.png / pause.png)
        self.btn_play_pause = self._create_icon_btn(
            self.media_controls_frame, "play", self.on_toggle_play, width=40, height=40,
            fg_color=("#1f538d", "#1DB954"), hover_color=("#14375e", "#1ed760")
        )
        self.btn_play_pause.pack(side="left", padx=6)

        # Stop (stop.png)
        self.btn_stop = self._create_icon_btn(
            self.media_controls_frame, "stop", self.on_stop, width=32, height=32
        )
        self.btn_stop.pack(side="left", padx=6)

        # Suivant (forward.png)
        self.btn_next = self._create_icon_btn(
            self.media_controls_frame, "forward", self.on_next, width=32, height=32
        )
        self.btn_next.pack(side="left", padx=6)

        # Répétition cyclique (no-repeat -> repeat-all -> repeat-one)
        self.btn_repeat = self._create_icon_btn(
            self.media_controls_frame, "no_repeat", self.on_toggle_repeat, width=32, height=32
        )
        self.btn_repeat.pack(side="left", padx=6)

        # Section Volume STRICTEMENT HORIZONTALE
        self.volume_frame = ctk.CTkFrame(self.row3_frame, fg_color="transparent")
        self.volume_frame.pack(side="right", padx=(10, 0))

        self.btn_mute = self._create_icon_btn(
            self.volume_frame, "volume_down", self.on_toggle_mute, width=30, height=30
        )
        self.btn_mute.pack(side="left", padx=(0, 6))

        self.slider_volume = ctk.CTkSlider(
            self.volume_frame,
            orientation="horizontal",
            from_=0,
            to=100,
            width=110,
            height=14,
            corner_radius=7,
            progress_color=("#1f538d", "#1DB954"),
            command=self.on_volume_changed
        )
        self.slider_volume.set(70)
        self.slider_volume.pack(side="left")

    def _create_icon_btn(self, parent, icon_key, command, width=32, height=32, fg_color="transparent", hover_color=None):
        if hover_color is None:
            hover_color = ("gray80", "#2E2E38")
        return ctk.CTkButton(
            parent,
            text="",
            image=self.icons.get(icon_key),
            width=width,
            height=height,
            corner_radius=height // 2,
            fg_color=fg_color,
            hover_color=hover_color,
            command=command
        )

    def toggle_lyrics_display(self):
        if self.app:
            if hasattr(self.app, "toggle_lyrics"):
                self.app.toggle_lyrics()
            elif hasattr(self.app, "show_lyrics_view") and hasattr(self.app, "show_previous_view"):
                if getattr(self.app, "current_view_name", "") == "lyrics":
                    self.app.show_previous_view()
                else:
                    self.app.show_lyrics_view(self.current_song)

    def on_toggle_play(self):
        if self.player_controller:
            if hasattr(self.player_controller, "toggle_play_pause"):
                self.player_controller.toggle_play_pause()
            elif hasattr(self.player_controller, "play") and hasattr(self.player_controller, "pause"):
                if self.is_playing:
                    self.player_controller.pause()
                else:
                    self.player_controller.play()
        self.is_playing = not self.is_playing
        self._update_play_pause_icon()

    def on_stop(self):
        if self.player_controller and hasattr(self.player_controller, "stop"):
            self.player_controller.stop()
        self.is_playing = False
        self.current_position = 0.0
        self.progress_slider.set(0)
        self.lbl_curr_time.configure(text="00:00")
        self._update_play_pause_icon()

    def on_previous(self):
        if self.queue_controller and hasattr(self.queue_controller, "previous"):
            self.queue_controller.previous()
        elif self.player_controller and hasattr(self.player_controller, "previous"):
            self.player_controller.previous()

    def on_next(self):
        if self.queue_controller and hasattr(self.queue_controller, "next"):
            self.queue_controller.next()
        elif self.player_controller and hasattr(self.player_controller, "next"):
            self.player_controller.next()

    def on_remove_from_queue(self):
        if self.current_song and self.queue_controller:
            song_id = getattr(self.current_song, "id", None)
            if song_id and hasattr(self.queue_controller, "remove_from_queue"):
                self.queue_controller.remove_from_queue(song_id)

    def on_toggle_favori(self):
        if not self.current_song:
            return
        song_id = getattr(self.current_song, "id", None)
        if not song_id:
            return

        is_fav = False
        if self.favori_controller:
            if hasattr(self.favori_controller, "toggle_favori"):
                is_fav = self.favori_controller.toggle_favori(song_id)
            elif hasattr(self.favori_controller, "is_favori"):
                current_status = self.favori_controller.is_favori(song_id)
                if current_status and hasattr(self.favori_controller, "remove_favori"):
                    self.favori_controller.remove_favori(song_id)
                    is_fav = False
                elif hasattr(self.favori_controller, "add_favori"):
                    self.favori_controller.add_favori(song_id)
                    is_fav = True
        self.set_favorite_state(is_fav)

    def on_toggle_repeat(self):
        modes = ["none", "all", "one"]
        next_idx = (modes.index(self.repeat_mode) + 1) % len(modes)
        self.repeat_mode = modes[next_idx]

        icon_map = {
            "none": "no_repeat",
            "all": "repeat_all",
            "one": "repeat_one"
        }
        self.btn_repeat.configure(image=self.icons.get(icon_map[self.repeat_mode]))

        if self.player_controller and hasattr(self.player_controller, "set_repeat_mode"):
            self.player_controller.set_repeat_mode(self.repeat_mode)

    def on_toggle_mute(self):
        if self.is_muted:
            self.slider_volume.set(self.previous_volume)
            self.on_volume_changed(self.previous_volume)
            self.btn_mute.configure(image=self.icons.get("volume_down"))
            self.is_muted = False
        else:
            self.previous_volume = self.slider_volume.get()
            self.slider_volume.set(0)
            self.on_volume_changed(0)
            self.btn_mute.configure(image=self.icons.get("volume_mute"))
            self.is_muted = True

    def on_volume_changed(self, value):
        vol = float(value)
        if vol == 0:
            self.btn_mute.configure(image=self.icons.get("volume_mute"))
        else:
            self.btn_mute.configure(image=self.icons.get("volume_down"))
            self.is_muted = False

        if self.player_controller and hasattr(self.player_controller, "set_volume"):
            self.player_controller.set_volume(vol / 100.0)

    def _on_seek_drag(self, value):
        self.is_seeking = True
        self.lbl_curr_time.configure(text=self._format_time(value))

    def _on_seek_release(self, event=None):
        target_sec = self.progress_slider.get()
        if self.player_controller and hasattr(self.player_controller, "seek"):
            self.player_controller.seek(target_sec)
        self.is_seeking = False

    def update_song(self, song):
        self.current_song = song
        if not song:
            self.lbl_track_info.configure(text="Aucun morceau en cours - Melodia-IA")
            self.lbl_total_time.configure(text="00:00")
            self.lbl_curr_time.configure(text="00:00")
            self.progress_slider.configure(to=100)
            self.progress_slider.set(0)
            self.btn_cover.configure(image=self.icons.get("default_cover"))
            self.set_favorite_state(False)
            return

        title = getattr(song, "title", "Titre inconnu") or "Titre inconnu"
        artist = getattr(song, "artist", "Artiste inconnu") or "Artiste inconnu"
        album = getattr(song, "album", "Album inconnu") or "Album inconnu"
        info_text = f"{title} - {artist} / {album}"
        self.lbl_track_info.configure(text=info_text)

        duration = getattr(song, "duration", 0) or 0
        self.current_duration = float(duration)
        self.lbl_total_time.configure(text=self._format_time(self.current_duration))
        self.progress_slider.configure(to=max(self.current_duration, 1.0))
        self.progress_slider.set(0)
        self.lbl_curr_time.configure(text="00:00")

        cover_path = getattr(song, "cover_path", None)
        if cover_path and os.path.exists(cover_path):
            try:
                img = Image.open(cover_path)
                ctk_img = ctk.CTkImage(light_image=img, dark_image=img, size=(68, 68))
                self.btn_cover.configure(image=ctk_img)
            except Exception:
                self.btn_cover.configure(image=self.icons.get("default_cover"))
        else:
            self.btn_cover.configure(image=self.icons.get("default_cover"))

        song_id = getattr(song, "id", None)
        if song_id and self.favori_controller and hasattr(self.favori_controller, "is_favori"):
            self.set_favorite_state(self.favori_controller.is_favori(song_id))
        else:
            self.set_favorite_state(False)

    def set_favorite_state(self, is_fav):
        icon_name = "favori" if is_fav else "not_favori"
        self.btn_favori.configure(image=self.icons.get(icon_name))

    def _update_play_pause_icon(self):
        icon_name = "pause" if self.is_playing else "play"
        self.btn_play_pause.configure(image=self.icons.get(icon_name))

    def _format_time(self, seconds):
        sec = max(0, int(seconds))
        mins = sec // 60
        secs = sec % 60
        return f"{mins:02d}:{secs:02d}"

    def _start_playback_poller(self):
        if self.player_controller:
            if hasattr(self.player_controller, "get_playback_position"):
                pos = self.player_controller.get_playback_position()
                if not self.is_seeking and self.is_playing:
                    self.current_position = pos
                    self.progress_slider.set(pos)
                    self.lbl_curr_time.configure(text=self._format_time(pos))
            if hasattr(self.player_controller, "is_playing"):
                playing = self.player_controller.is_playing()
                if playing != self.is_playing:
                    self.is_playing = playing
                    self._update_play_pause_icon()

        self.after(200, self._start_playback_poller)