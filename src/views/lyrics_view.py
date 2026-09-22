"""
Melodia-IA - Vue des Paroles Synchronisées (LyricsView)
Architecture MVC - Vue affichée dans la zone centrale (main_frame) de l'application.
Implémentation CustomTkinter (ctk) avec fallback Tkinter.
"""

import os
from PIL import Image, ImageTk
from controllers.player_controller import player_controller
from controllers.lyrics_controller import lyrics_controller
from views.lyrics_editor_dialog import LyricsEditorDialog

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
    def __init__(self, parent, app=None, **kwargs):
        if USE_CTK:
            kwargs.setdefault("fg_color", ("#F9F9FB", "#0F0F14"))
            kwargs.setdefault("corner_radius", 0)
        super().__init__(parent, **kwargs)

        self.app = app

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

        # Bouton d'édition (import .lrc / saisie manuelle) - toujours à
        # droite de l'en-tête, actif dès qu'un morceau est chargé. Empaqueté
        # avant le cadre extensible ci-dessous pour garder sa place.
        self.btn_edit = ctk.CTkButton(
            self.header_frame,
            text="✎ Modifier les paroles",
            width=150,
            height=32,
            fg_color="transparent",
            border_width=1,
            text_color=("gray20", "#EAEAEA"),
            hover_color=("gray85", "#1F1F28"),
            command=self._open_lyrics_editor,
            state="disabled"
        )
        self.btn_edit.pack(side="right", padx=(10, 0))

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

    def _open_lyrics_editor(self):
        if self.current_song is None:
            return
        LyricsEditorDialog(self, self.current_song, on_saved=self._on_lyrics_saved)

    def _on_lyrics_saved(self):
        # Recharge les paroles du morceau courant pour refléter ce qui
        # vient d'être importé/édité et enregistré côté backend.
        if self.current_song is not None:
            self.load_song(self.current_song)

    def refresh(self):
        """Recharge le morceau courant et ses paroles depuis le backend.
        Appelé à chaque ouverture de la vue (clic sur la pochette), pour
        être certain d'afficher l'état réel du lecteur même si le morceau
        a changé pendant que la vue était masquée."""
        self._sync_current_song(force=True)

    def _sync_current_song(self, force=False):
        song = player_controller.current_song()
        if song is None:
            self.load_song(None)
            return
        if force or self._get_song_id(song) != self._get_song_id(self.current_song):
            self.load_song(song)

    def _get_song_id(self, song):
        if song is None:
            return None
        return getattr(song, "id", None)

    def load_song(self, song):
        self.current_song = song
        self.active_line_index = -1
        self.current_time = 0.0

        if not song:
            self.lbl_title.configure(text="Paroles - Aucun morceau")
            self.lbl_artist_album.configure(text="Sélectionnez un titre pour synchroniser")
            self.btn_edit.configure(state="disabled")
            self._render_empty_state("Aucun morceau sélectionné.")
            return

        title = song.title or "Titre inconnu"
        artist = ", ".join(song.artists) if song.artists else "Artiste inconnu"
        album = song.album or "Album inconnu"

        self.lbl_title.configure(text=f"{title}")
        self.lbl_artist_album.configure(text=f"{artist} • {album}")
        self.btn_edit.configure(state="normal")

        parsed = lyrics_controller.get_parsed_lyrics(song.id)
        if parsed:
            self._display_synced_lyrics(parsed)
            return

        raw = lyrics_controller.get_lyrics(song.id)
        if raw:
            self._display_raw_lyrics(raw)
        else:
            self._render_empty_state(
                "Aucune parole pour ce morceau.\n"
                "Cliquez sur \"Modifier les paroles\" pour en importer ou en saisir."
            )

    def _display_raw_lyrics(self, raw_lines):
        """Affiche des paroles présentes mais pas encore synchronisées
        (aucune ligne au format [mm:ss.xx]) : simple liste de texte, sans
        surlignage ni défilement automatique, en attendant la
        synchronisation (prochaine étape)."""
        for widget in self.lyrics_container.winfo_children():
            widget.destroy()
        self.lines = []

        info = ctk.CTkLabel(
            self.lyrics_container,
            text="Paroles non synchronisées — la lecture ne suit pas encore ces lignes.",
            font=ctk.CTkFont(family="Segoe UI", size=12),
            text_color=("gray45", "#A8A8B2"),
            justify="center"
        )
        info.pack(pady=(0, 12))

        for raw in raw_lines:
            text = raw.strip()
            if not text:
                continue
            lbl = ctk.CTkLabel(
                self.lyrics_container,
                text=text,
                font=ctk.CTkFont(family="Segoe UI", size=15),
                text_color=("gray30", "#C8C8D0"),
                justify="center"
            )
            lbl.pack(fill="x", pady=3, padx=10)

    def _display_synced_lyrics(self, parsed):
        for widget in self.lyrics_container.winfo_children():
            widget.destroy()

        self.lines = []
        if not parsed:
            self._render_empty_state("Aucune parole synchronisée (.lrc) trouvée pour ce morceau.")
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
        try:
            player_controller.seek(time_sec)
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

            if self.auto_scroll_enabled and 0 <= active_idx < len(self.lines) and USE_CTK:
                try:
                    canvas = self.scroll_lyrics._parent_canvas
                    fraction = active_idx / max(len(self.lines) - 1, 1)
                    canvas.yview_moveto(max(0.0, min(1.0, fraction)))
                except Exception:
                    pass

    def _start_lyrics_poller(self):
        # Rien à faire tant que la vue n'est pas réellement affichée
        # (elle est superposée par App, masquée par grid_forget sinon).
        if not self.winfo_ismapped():
            self._poller_id = self.after(200, self._start_lyrics_poller)
            return

        try:
            self._sync_current_song()
            position = player_controller.get_playback_position()
            if position is not None:
                self.update_playback_position(float(position))
        except Exception as e:
            print(f"[LyricsView] Erreur synchro paroles: {e}")

        self._poller_id = self.after(200, self._start_lyrics_poller)

    def destroy(self):
        if self._poller_id:
            try:
                self.after_cancel(self._poller_id)
            except Exception:
                pass
        super().destroy()