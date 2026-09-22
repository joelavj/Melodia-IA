"""
Melodia-IA - Vue des Paroles Synchronisées (LyricsView)
Architecture MVC - Vue affichée dans la zone centrale (main_frame) de l'application.
Implémentation CustomTkinter (ctk) avec fallback Tkinter.
"""

import os
import re
from PIL import Image, ImageTk

try:
    import customtkinter as ctk
    BASE_FRAME = ctk.CTkFrame
    SCROLL_FRAME = ctk.CTkScrollableFrame
    USE_CTK = True
except ImportError:
    import tkinter as ctk
    BASE_FRAME = ctk.Frame
    SCROLL_FRAME = ctk.Frame
    USE_CTK = False


class LyricsView(BASE_FRAME):
    def __init__(self, parent, app=None, player_controller=None, lyrics_controller=None, **kwargs):
        if USE_CTK:
            kwargs.setdefault("fg_color", ("#F9F9FB", "#0F0F14"))
            kwargs.setdefault("corner_radius", 0)
        super().__init__(parent, **kwargs)

        self.app = app
        self.player_controller = player_controller
        self.lyrics_controller = lyrics_controller

        # État interne
        self.current_song = None
        self.current_time = 0.0
        self.lines = []  # Liste de dicts: [{'time': float, 'text': str, 'widget': widget}]
        self.active_line_index = -1
        self.auto_scroll_enabled = True

        # Répertoire des icônes
        self.assets_dir = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "..", "assets")
        )

        # Cache d'icônes
        self.icons = {}
        self._load_all_icons()

        # Interface
        self._setup_ui()

        # Poller de synchronisation des paroles
        self._poller_id = None
        self._start_lyrics_poller()

        self._sync_current_song()

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
            print(f"[LyricsView] Erreur chargement icône {filename}: {e}")
            return None

    def _load_all_icons(self):
        icon_specs = {
            "back": ("en-arriere.png", (22, 22)),
            "default_cover": ("melodia_ia.png", (48, 48)),
        }
        for key, (fname, sz) in icon_specs.items():
            self.icons[key] = self._load_icon(fname, sz)

    def _setup_ui(self):
        # 1. EN-TÊTE : Bouton Retour + Informations Morceau
        self.header_frame = ctk.CTkFrame(self, fg_color="transparent", height=60)
        self.header_frame.pack(fill="x", padx=20, pady=(15, 10))

        # Bouton Retour (en-arriere.png)
        self.btn_back = ctk.CTkButton(
            self.header_frame,
            text="",
            image=self.icons.get("back"),
            width=40,
            height=40,
            corner_radius=20,
            fg_color=("gray85", "#1F1F28"),
            hover_color=("gray75", "#2C2C38"),
            command=self.on_back_clicked
        )
        self.btn_back.pack(side="left", padx=(0, 15))

        # Informations Titre & Artiste
        self.track_info_frame = ctk.CTkFrame(self.header_frame, fg_color="transparent")
        self.track_info_frame.pack(side="left", fill="both", expand=True)

        self.lbl_title = ctk.CTkLabel(
            self.track_info_frame,
            text="Paroles - Aucun morceau",
            font=ctk.CTkFont(family="Segoe UI", size=16, weight="bold"),
            anchor="w",
            text_color=("gray10", "#FFFFFF")
        )
        self.lbl_title.pack(anchor="w")

        self.lbl_artist_album = ctk.CTkLabel(
            self.track_info_frame,
            text="Sélectionnez un titre pour synchroniser",
            font=ctk.CTkFont(family="Segoe UI", size=12),
            anchor="w",
            text_color=("gray40", "#A0A0B0")
        )
        self.lbl_artist_album.pack(anchor="w")

        # 2. ZONE CENTRALE DÉFILANTE : Paroles Synchronisées
        if USE_CTK:
            self.scroll_lyrics = ctk.CTkScrollableFrame(
                self,
                fg_color="transparent",
                scrollbar_button_color=("#1DB954", "#1DB954"),
                scrollbar_button_hover_color=("#1ED760", "#1ED760")
            )
        else:
            self.scroll_lyrics = ctk.Frame(self, bg="#0F0F14")
        self.scroll_lyrics.pack(fill="both", expand=True, padx=30, pady=(10, 20))

        # Conteneur des lignes de paroles
        self.lyrics_container = ctk.CTkFrame(self.scroll_lyrics, fg_color="transparent")
        self.lyrics_container.pack(fill="both", expand=True)

        self.lbl_empty_state = ctk.CTkLabel(
            self.lyrics_container,
            text="Aucune parole disponible pour ce morceau.\nCliquez sur la pochette en bas pour revenir.",
            font=ctk.CTkFont(family="Segoe UI", size=14),
            text_color=("gray50", "#707080"),
            justify="center"
        )
        self.lbl_empty_state.pack(expand=True, pady=100)

    def on_back_clicked(self):
        if self.app:
            if hasattr(self.app, "show_previous_view"):
                self.app.show_previous_view()
            elif hasattr(self.app, "toggle_lyrics"):
                self.app.toggle_lyrics()
            elif hasattr(self.app, "switch_view"):
                prev = getattr(self.app, "previous_view", "acceuil")
                self.app.switch_view(prev)

    def _sync_current_song(self):
        song = None
        for src in (self.player_controller, self.app):
            if not src:
                continue
            for attr in ("current_song", "get_current_song", "now_playing", "current_track"):
                val = getattr(src, attr, None)
                if callable(val):
                    try:
                        res = val()
                        if res:
                            song = res
                            break
                    except Exception:
                        pass
                elif val:
                    song = val
                    break
            if song:
                break

        if song:
            self.load_song(song)

    def load_song(self, song):
        self.current_song = song
        self.active_line_index = -1

        if not song:
            self.lbl_title.configure(text="Paroles - Aucun morceau")
            self.lbl_artist_album.configure(text="Sélectionnez un titre pour synchroniser")
            self._render_empty_state("Aucun morceau sélectionné.")
            return

        if isinstance(song, dict):
            title = song.get("title") or "Titre inconnu"
            artist = song.get("artist") or "Artiste inconnu"
            album = song.get("album") or "Album inconnu"
            lrc_content = song.get("lrcContent") or song.get("lyrics") or ""
            song_path = song.get("path") or song.get("file_path") or ""
        else:
            title = getattr(song, "title", "Titre inconnu") or "Titre inconnu"
            artist = getattr(song, "artist", "Artiste inconnu") or "Artiste inconnu"
            album = getattr(song, "album", "Album inconnu") or "Album inconnu"
            lrc_content = getattr(song, "lrcContent", "") or getattr(song, "lyrics", "")
            song_path = getattr(song, "path", "") or getattr(song, "file_path", "")

        self.lbl_title.configure(text=f"{title}")
        self.lbl_artist_album.configure(text=f"{artist} • {album}")

        if not lrc_content and song_path:
            base_no_ext = os.path.splitext(song_path)[0]
            lrc_path = base_no_ext + ".lrc"
            if os.path.exists(lrc_path):
                try:
                    with open(lrc_path, "r", encoding="utf-8") as f:
                        lrc_content = f.read()
                except Exception:
                    pass

        self._parse_and_display_lyrics(lrc_content)

    def _parse_and_display_lyrics(self, lrc_text):
        for widget in self.lyrics_container.winfo_children():
            widget.destroy()

        self.lines = []
        if not lrc_text or not lrc_text.strip():
            self._render_empty_state("Aucune parole synchronisée (.lrc) trouvée pour ce morceau.")
            return

        raw_lines = lrc_text.splitlines()
        time_regex = re.compile(r"\[(\d{2}):(\d{2})(?:\.(\d{2,3}))?\]")

        parsed = []
        for raw in raw_lines:
            raw_s = raw.strip()
            if not raw_s:
                continue
            matches = list(time_regex.finditer(raw_s))
            if matches:
                clean_text = time_regex.sub("", raw_s).strip()
                if not clean_text:
                    continue
                for m in matches:
                    mins = int(m.group(1))
                    secs = int(m.group(2))
                    ms_str = m.group(3) or "0"
                    ms = int(ms_str.ljust(3, '0')[:3])
                    total_sec = mins * 60 + secs + (ms / 1000.0)
                    parsed.append({"time": total_sec, "text": clean_text})
            else:
                parsed.append({"time": 0.0, "text": raw_s})

        parsed.sort(key=lambda x: x["time"])

        if not parsed:
            self._render_empty_state("Aucune ligne de parole valide détectée.")
            return

        for idx, item in enumerate(parsed):
            line_time = item["time"]
            line_text = item["text"]

            line_btn = ctk.CTkButton(
                self.lyrics_container,
                text=line_text,
                font=ctk.CTkFont(family="Segoe UI", size=15),
                text_color=("gray45", "#707080"),
                fg_color="transparent",
                hover_color=("gray85", "#1C1C24"),
                anchor="center",
                corner_radius=8,
                command=lambda t=line_time: self.seek_to_lyric_time(t)
            )
            line_btn.pack(fill="x", pady=4, padx=10)
            self.lines.append({"time": line_time, "text": line_text, "widget": line_btn})

    def _render_empty_state(self, message):
        self.lbl_empty_state = ctk.CTkLabel(
            self.lyrics_container,
            text=message,
            font=ctk.CTkFont(family="Segoe UI", size=14),
            text_color=("gray50", "#707080"),
            justify="center"
        )
        self.lbl_empty_state.pack(expand=True, pady=100)

    def seek_to_lyric_time(self, time_sec):
        if self.player_controller and hasattr(self.player_controller, "seek"):
            try:
                self.player_controller.seek(time_sec)
            except Exception as e:
                print(f"[LyricsView] Erreur seek: {e}")

    def update_playback_position(self, current_sec):
        if not self.lines:
            return

        self.current_time = current_sec

        active_idx = -1
        for idx, line in enumerate(self.lines):
            if current_sec >= line["time"]:
                active_idx = idx
            else:
                break

        if active_idx != self.active_line_index:
            if 0 <= self.active_line_index < len(self.lines):
                prev_btn = self.lines[self.active_line_index]["widget"]
                if prev_btn.winfo_exists():
                    prev_btn.configure(
                        text_color=("gray45", "#707080"),
                        font=ctk.CTkFont(family="Segoe UI", size=15),
                        fg_color="transparent"
                    )

            if 0 <= active_idx < len(self.lines):
                curr_btn = self.lines[active_idx]["widget"]
                if curr_btn.winfo_exists():
                    curr_btn.configure(
                        text_color=("#1DB954", "#1ED760"),
                        font=ctk.CTkFont(family="Segoe UI", size=18, weight="bold"),
                        fg_color=("gray90", "#181822")
                    )

            self.active_line_index = active_idx

    def _start_lyrics_poller(self):
        try:
            curr_song = None
            for src in (self.player_controller, self.app):
                if not src:
                    continue
                for attr in ("current_song", "get_current_song", "now_playing"):
                    v = getattr(src, attr, None)
                    if callable(v):
                        try:
                            curr_song = v()
                        except Exception:
                            pass
                    elif v:
                        curr_song = v
                    if curr_song:
                        break
                if curr_song:
                    break

            if curr_song and curr_song != self.current_song:
                c_id = getattr(curr_song, "id", None) if not isinstance(curr_song, dict) else curr_song.get("id")
                p_id = getattr(self.current_song, "id", None) if not isinstance(self.current_song, dict) else (self.current_song.get("id") if self.current_song else None)
                if c_id != p_id:
                    self.load_song(curr_song)

            if self.player_controller:
                for pos_method in ("get_playback_position", "get_position", "get_time"):
                    if hasattr(self.player_controller, pos_method):
                        try:
                            pos = getattr(self.player_controller, pos_method)()
                            if pos is not None:
                                self.update_playback_position(float(pos))
                            break
                        except Exception:
                            pass
        except Exception:
            pass

        self._poller_id = self.after(200, self._start_lyrics_poller)

    def destroy(self):
        if self._poller_id:
            try:
                self.after_cancel(self._poller_id)
            except Exception:
                pass
        super().destroy()