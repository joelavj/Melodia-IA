"""
Melodia-IA - Barre de pilote de lecture (PlayerBar)
Architecture MVC - Vue du lecteur audio située en bas de l'application.
Implémentation CustomTkinter (ctk) avec disposition centrée et harmonieuse.
"""

import os
import math
from PIL import Image, ImageTk
from controllers.player_controller import player_controller
from controllers.queue_controller import queue_controller
from controllers.favori_controller import favori_controller
from controllers.lyrics_controller import lyrics_controller

try:
    import customtkinter as ctk
    BASE_FRAME = ctk.CTkFrame
    USE_CTK = True
except ImportError:
    import tkinter as ctk
    BASE_FRAME = ctk.Frame
    USE_CTK = False


class PlayerBar(BASE_FRAME):
    def __init__(self, parent, app=None, **kwargs):
        if USE_CTK:
            kwargs.setdefault("fg_color", ("#F2F2F5", "#18181C"))
            kwargs.setdefault("height", 112)
            kwargs.setdefault("corner_radius", 0)
        super().__init__(parent, **kwargs)

        self.app = app

        # État interne du lecteur
        self.is_playing = False
        self.is_seeking = False
        self.current_song = player_controller.current_song()
        self.current_duration = 0.0
        self.current_position = 0.0
        self.is_muted = False
        self.previous_volume = 70.0
        self.repeat_mode = "none"  # "none", "all", "one"
        self.is_in_lyrics_view = False

        # Résolution du dossier des icônes assets
        self.assets_dir = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "..", "assets")
        )

        # Cache d'icônes
        self.icons = {}
        self._load_all_icons()

        # Construction de l'interface centrée
        self._setup_ui()

        # Démarrage de la boucle de synchronisation temporelle avec le backend
        self._poller_id = None
        self._start_playback_poller()

        self._sync_initial_state()

    def _get_song_id(self, song):
        """Extrait l'identifiant d'un morceau, que ce soit un objet Song
        (attribut `id`) ou un dict (`id`/`song_id`). Centralisé ici pour
        éviter les divergences entre les différents endroits du fichier
        qui avaient chacun leur propre variante de cette logique."""
        if song is None:
            return None
        if isinstance(song, dict):
            return song.get("id") or song.get("song_id")
        return getattr(song, "id", None) or getattr(song, "song_id", None)

    def _load_icon(self, filename, size=(22, 22)):
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
            print(f"[PlayerBar] Erreur de chargement d'icône {filename}: {e}")
            return None

    def _load_all_icons(self):
        icon_specs = {
            "play": ("play.png", (22, 22)),
            "pause": ("pause.png", (22, 22)),
            "stop": ("stop.png", (18, 18)),
            "rewind": ("rewind.png", (18, 18)),
            "forward": ("forward.png", (18, 18)),
            "favori": ("favori.png", (18, 18)),
            "not_favori": ("not-favori.png", (18, 18)),
            "cross": ("cross.png", (16, 16)),
            "no_repeat": ("no-repeat.png", (18, 18)),
            "repeat_all": ("repeat-all.png", (18, 18)),
            "repeat_one": ("repeat-one.png", (18, 18)),
            "volume_down": ("volume-down.png", (18, 18)),
            "volume_mute": ("volume-mute.png", (18, 18)),
            "default_cover": ("melodia_ia.png", (60, 60)),
        }
        for key, (fname, sz) in icon_specs.items():
            self.icons[key] = self._load_icon(fname, sz)

    def _setup_ui(self):
        self.pack_propagate(False)

        # 1. ZONE GAUCHE : Pochette cliquable (Album Cover)
        self.cover_frame = ctk.CTkFrame(self, fg_color="transparent", width=84, height=84)
        self.cover_frame.pack(side="left", padx=(16, 8), pady=12)
        self.cover_frame.pack_propagate(False)

        self.btn_cover = ctk.CTkButton(
            self.cover_frame,
            text="",
            image=self.icons.get("default_cover"),
            width=68,
            height=68,
            corner_radius=8,
            fg_color=("gray85", "#26262E"),
            hover_color=("gray75", "#32323D"),
            command=self.toggle_lyrics_display
        )
        self.btn_cover.pack(fill="both", expand=True)

        # 2. ZONE DROITE : Contrôle de Volume Horizontal
        self.volume_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.volume_frame.pack(side="right", padx=(8, 20), pady=12)

        self.btn_mute = ctk.CTkButton(
            self.volume_frame,
            text="",
            image=self.icons.get("volume_down"),
            width=28,
            height=28,
            corner_radius=14,
            fg_color="transparent",
            hover_color=("gray80", "#2E2E38"),
            command=self.on_toggle_mute
        )
        self.btn_mute.pack(side="left", padx=(0, 6))

        self.slider_volume = ctk.CTkSlider(
            self.volume_frame,
            orientation="horizontal",
            from_=0,
            to=100,
            width=100,
            height=12,
            corner_radius=6,
            progress_color=("#1f538d", "#1DB954"),
            button_color=("#1f538d", "#1DB954"),
            button_hover_color=("#14375e", "#1ED760"),
            button_length=10,
            command=self.on_volume_changed
        )
        self.slider_volume.set(70)
        self.slider_volume.pack(side="left")

        # 3. ZONE CENTRALE : Informations, Barre de progression et Contrôles
        self.center_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.center_frame.pack(side="left", fill="both", expand=True, padx=8, pady=6)

        # LIGNE 1 : Titre morceau - Nom artiste / Album (Centré)
        self.lbl_track_info = ctk.CTkLabel(
            self.center_frame,
            text="Aucun morceau en cours - Melodia-IA",
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            anchor="center",
            text_color=("gray20", "#FFFFFF")
        )
        self.lbl_track_info.pack(fill="x", pady=(2, 3))

        # LIGNE 2 : Conteneur centré pour le Seek & Temps
        self.seek_container = ctk.CTkFrame(self.center_frame, fg_color="transparent")
        self.seek_container.pack(fill="x", pady=(1, 3))

        # Sous-cadre centré avec largeur modérée (360px)
        self.seek_subframe = ctk.CTkFrame(self.seek_container, fg_color="transparent")
        self.seek_subframe.pack(anchor="center")

        self.lbl_curr_time = ctk.CTkLabel(
            self.seek_subframe,
            text="00:00",
            width=42,
            font=ctk.CTkFont(family="Segoe UI", size=11),
            text_color=("gray40", "#A8A8B2")
        )
        self.lbl_curr_time.pack(side="left", padx=(0, 8))

        self.progress_slider = ctk.CTkSlider(
            self.seek_subframe,
            from_=0,
            to=100,
            width=360,
            height=10,
            corner_radius=5,
            progress_color=("#1f538d", "#1DB954"),
            button_color=("#1f538d", "#1DB954"),
            button_hover_color=("#14375e", "#1ED760"),
            button_length=10,
            command=lambda value: self._on_seek_drag(value)
        )
        self.progress_slider.set(0)
        self.progress_slider.pack(side="left")
        self.progress_slider.bind("<ButtonPress-1>", self._on_seek_press)
        self.progress_slider.bind("<ButtonRelease-1>", self._on_seek_release)

        self.lbl_total_time = ctk.CTkLabel(
            self.seek_subframe,
            text="00:00",
            width=42,
            font=ctk.CTkFont(family="Segoe UI", size=11),
            text_color=("gray40", "#A8A8B2")
        )
        self.lbl_total_time.pack(side="left", padx=(8, 0))

        # LIGNE 3 : Pilotes de lecture (Centrés sous la barre de progression)
        self.media_controls_frame = ctk.CTkFrame(self.center_frame, fg_color="transparent")
        self.media_controls_frame.pack(anchor="center", pady=(2, 2))

        # Retirer de la file d'attente (cross.png)
        self.btn_remove_queue = self._create_icon_btn(
            self.media_controls_frame, "cross", command=self.on_remove_from_queue, width=30, height=30
        )
        self.btn_remove_queue.pack(side="left", padx=4)

        # Favori dynamique (favori.png / not-favori.png)
        self.btn_favori = self._create_icon_btn(
            self.media_controls_frame, "not_favori", command=self.on_toggle_favori, width=30, height=30
        )
        self.btn_favori.pack(side="left", padx=4)

        # Précédent (rewind.png)
        self.btn_prev = self._create_icon_btn(
            self.media_controls_frame, "rewind", command=self.on_previous, width=32, height=32
        )
        self.btn_prev.pack(side="left", padx=5)

        # Play / Pause dynamique mis en avant (play.png / pause.png)
        self.btn_play_pause = self._create_icon_btn(
            self.media_controls_frame, "play", command=self.on_toggle_play, width=38, height=38,
            fg_color=("#1f538d", "#1DB954"), hover_color=("#14375e", "#1ED760")
        )
        self.btn_play_pause.pack(side="left", padx=6)

        # Stop (stop.png)
        self.btn_stop = self._create_icon_btn(
            self.media_controls_frame, "stop", command=self.on_stop, width=32, height=32
        )
        self.btn_stop.pack(side="left", padx=5)

        # Suivant (forward.png)
        self.btn_next = self._create_icon_btn(
            self.media_controls_frame, "forward", command=self.on_next, width=32, height=32
        )
        self.btn_next.pack(side="left", padx=5)

        # Répétition cyclique (no-repeat -> repeat-all -> repeat-one)
        self.btn_repeat = self._create_icon_btn(
            self.media_controls_frame, "no_repeat", command=self.on_toggle_repeat, width=30, height=30
        )
        self.btn_repeat.pack(side="left", padx=4)

    def _create_icon_btn(self, parent, icon_key, command, width=30, height=30, fg_color="transparent", hover_color=None):
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

    # --- LIAISONS BACKEND ---
    def _sync_initial_state(self):
        song = player_controller.current_song()
        if song:
            self.update_song()

        if player_controller and hasattr(player_controller, "get_repeat_mode"):
            try:
                backend_mode = player_controller.get_repeat_mode()
                if backend_mode is not None:
                    self.repeat_mode = self._normalize_repeat_mode(backend_mode)
                    icon_map = {
                        "none": "no_repeat",
                        "all": "repeat_all",
                        "one": "repeat_one"
                    }
                    self.btn_repeat.configure(image=self.icons.get(icon_map.get(self.repeat_mode, "no_repeat")))
            except Exception as e:
                print(f"[PlayerBar] Erreur get_repeat_mode: {e}")
       

    def toggle_lyrics_display(self):
        song = self.current_song or player_controller.current_song()
        if self.app:
            if hasattr(self.app, "toggle_lyrics"):
                self.app.toggle_lyrics()
            elif hasattr(self.app, "show_lyrics_view") and hasattr(self.app, "show_previous_view"):
                if getattr(self.app, "current_view_name", "") == "lyrics":
                    self.app.show_previous_view()
                else:
                    self.app.show_lyrics_view(song)
            elif hasattr(self.app, "switch_view"):
                curr = getattr(self.app, "current_view", "")
                if curr == "lyrics":
                    prev = getattr(self.app, "previous_view", "accueil")
                    self.app.switch_view(prev)
                else:
                    self.app.switch_view("lyrics")

    def on_toggle_play(self):
        player_controller.play_song()
        self.is_playing = player_controller.is_playing()
        self._update_play_pause_icon()
        return


    def on_stop(self):
        player_controller.stop()
        self.is_playing = False
        self.current_position = 0.0
        self.progress_slider.set(0)
        self.lbl_curr_time.configure(text="00:00")
        self._update_play_pause_icon()
        self.update_song()


    def on_previous(self):
        player_controller.previous_song()
        self.update_song()
        self._update_play_pause_icon()
        return

    def on_next(self):
        player_controller.next_song()
        self.update_song()
        self._update_play_pause_icon()
        return

    def on_remove_from_queue(self):
        song = player_controller.current_song()
        if song is not None:
            queue_controller.remove_song(song.id)
            self.update_song()

    
    def on_toggle_favori(self):
        song = player_controller.current_song()
        if song is None:
            return
        new_state = not song.favori
        if song.favori:
            favori_controller.remove_favori(song.id)
        else:
            favori_controller.add_favori(song.id)
        # song.favori n'est jamais réécrit par les appels ci-dessus (ils ne
        # touchent que la base) : relire song.favori ensuite renvoyait donc
        # toujours l'ancienne valeur, et l'icône ne changeait jamais. On met
        # à jour l'objet en cache et on utilise l'état nouvellement calculé.
        song.favori = new_state
        self.set_favorite_state(new_state)
    

    def _normalize_repeat_mode(self, mode):
        """Convertit la valeur de mode répétition renvoyée par le backend
        (enum, string, etc.) vers l'une des clés internes 'none'/'all'/'one'."""
        name = getattr(mode, "name", None) or str(mode)
        name = name.lower()
        if "one" in name or "single" in name:
            return "one"
        if "all" in name:
            return "all"
        return "none"

    def on_toggle_repeat(self):
        new_mode = None
        if player_controller and hasattr(player_controller, "change_repeat_mode"):
            try:
                new_mode = player_controller.change_repeat_mode()
            except Exception as e:
                print(f"[PlayerBar] Erreur change_repeat_mode: {e}")

        if new_mode is not None:
            self.repeat_mode = self._normalize_repeat_mode(new_mode)
        else:
            modes = ["none", "all", "one"]
            next_idx = (modes.index(self.repeat_mode) + 1) % len(modes)
            self.repeat_mode = modes[next_idx]

        icon_map = {
            "none": "no_repeat",
            "all": "repeat_all",
            "one": "repeat_one"
        }
        self.btn_repeat.configure(image=self.icons.get(icon_map.get(self.repeat_mode, "no_repeat")))

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
        try:
            vol = float(value)
        except (ValueError, TypeError):
            vol = 0.0

        if vol <= 0:
            self.btn_mute.configure(image=self.icons.get("volume_mute"))
        else:
            self.btn_mute.configure(image=self.icons.get("volume_down"))
            self.is_muted = False

        if player_controller and hasattr(player_controller, "set_volume"):
            try:
                player_controller.set_volume(vol / 100.0)
            except Exception as e:
                print(f"[PlayerBar] Erreur set_volume: {e}")

    def _on_seek_press(self, event=None):
        self.is_seeking = True

    def _on_seek_drag(self, value):
        self.is_seeking = True
        try:
            val_sec = float(value)
        except (ValueError, TypeError):
            val_sec = 0.0
        self.lbl_curr_time.configure(text=self._format_time(val_sec))

    def _on_seek_release(self, event=None):
        target_sec = self.progress_slider.get()
        if player_controller and hasattr(player_controller, "seek"):
            try:
                player_controller.seek(int(target_sec))
                self.current_position = target_sec
            except Exception as e:
                print(f"[PlayerBar] Erreur seek: {e}")
        self.is_seeking = False
        

    def update_song(self):
        self.current_song = player_controller.current_song()
        if self.current_song is None:
            self.lbl_track_info.configure(text="Aucun morceau en cours - Melodia-IA")
            self.lbl_total_time.configure(text="00:00")
            self.lbl_curr_time.configure(text="00:00")
            self.progress_slider.configure(to=100)
            self.progress_slider.set(0)
            self.btn_cover.configure(image=self.icons.get("default_cover"))
            self.current_song_favori = False
            self.set_favorite_state(False)
            return

        title = self.current_song.title
        artist = ", ".join(self.current_song.artists)
        album = self.current_song.album
        duration = self.current_song.duration
        cover_path = self.current_song.cover_path
        song_id = self.current_song.id
        is_fav = self.current_song.favori
        
        self.lbl_track_info.configure(text=f"{title} - {artist} / {album}")

        try:
            self.current_duration = float(duration)
        except Exception:
            self.current_duration = 0.0

        self.lbl_total_time.configure(text=self._format_time(self.current_duration))
        self.progress_slider.configure(to=max(self.current_duration, 1.0))
        self.progress_slider.set(0)
        self.lbl_curr_time.configure(text="00:00")

        if cover_path and os.path.exists(cover_path):
            try:
                pil_img = Image.open(cover_path)
                if USE_CTK:
                    ctk_img = ctk.CTkImage(light_image=pil_img, dark_image=pil_img, size=(68, 68))
                    self.btn_cover.configure(image=ctk_img)
                else:
                    resized = pil_img.resize((68, 68), Image.Resampling.LANCZOS)
                    tk_img = ImageTk.PhotoImage(resized)
                    self.btn_cover.configure(image=tk_img)
            except Exception:
                self.btn_cover.configure(image=self.icons.get("default_cover"))
        else:
            self.btn_cover.configure(image=self.icons.get("default_cover"))

        self.current_song_favori = is_fav
        self.set_favorite_state(is_fav)

    def set_favorite_state(self, is_fav):
        icon_name = "favori" if is_fav else "not_favori"
        self.btn_favori.configure(image=self.icons.get(icon_name))

    def _update_play_pause_icon(self):
        icon_name = "pause" if player_controller.is_playing() else "play"
        self.btn_play_pause.configure(image=self.icons.get(icon_name))

    def _format_time(self, seconds):
        sec = max(0, int(seconds))
        mins = sec // 60
        secs = sec % 60
        return f"{mins:02d}:{secs:02d}"

    def _start_playback_poller(self):
        player_controller.process_event()

        new_song = player_controller.current_song()
        if self._get_song_id(new_song) != self._get_song_id(self.current_song):
            # Le morceau courant a changé (next/previous manuel, fin de
            # morceau auto, suppression du morceau en cours, ...) : on
            # rafraîchit l'ensemble de l'affichage (titre, pochette, durée,
            # état favori, remise à zéro de la barre).
            self.update_song()
            self._update_play_pause_icon()
        else:
            # Même morceau : on se contente d'avancer le curseur de
            # progression avec la position réelle renvoyée par le backend,
            # sans jamais l'écraser à 0. On ignore ce tick pendant que
            # l'utilisateur fait glisser le curseur lui-même.
            self._update_playback_position()

        self._poller_id = self.after(200, self._start_playback_poller)

    def _update_playback_position(self):
        if self.current_song is None or self.is_seeking:
            return
        if not player_controller.is_playing():
            # En pause ou à l'arrêt : on laisse le curseur là où il est au
            # lieu de le faire bouger avec une position backend obsolète.
            return
        try:
            pos = player_controller.get_playback_position()
        except Exception:
            return
        pos = max(0.0, pos)
        if self.current_duration:
            pos = min(pos, self.current_duration)
        self.current_position = pos
        self.progress_slider.set(pos)
        self.lbl_curr_time.configure(text=self._format_time(pos))


    def destroy(self):
        if self._poller_id:
            try:
                self.after_cancel(self._poller_id)
            except Exception:
                pass
        super().destroy()