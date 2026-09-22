import tkinter as tk
import customtkinter as ctk

from utils.function import load_image
from utils.constante import BASE_DIR
from controllers.library_controller import library_controller
from controllers.queue_controller import queue_controller
from controllers.player_controller import player_controller
from views.menu_actions import build_song_context_menu


class QueueSongRow(tk.Frame):
    """Ligne de la file d'attente : réutilise le menu ⋮ commun et ajoute
    les flèches de réordonnancement + le retrait du morceau, avec un style
    distinct pour le morceau en cours de lecture."""

    def __init__(self, parent, index, song, is_current,
                 on_play, on_remove, on_move_up, on_move_down):
        bg = "#215b52" if is_current else "#2d2d2d"
        super().__init__(parent, bg=bg, height=56)
        self.pack_propagate(False)

        self.id_song = song.id
        self.favori = bool(getattr(song, "favori", False))
        artists = ", ".join(song.artists) if isinstance(song.artists, list) else song.artists
        self.title = song.title
        self.artists = artists
        self.album = song.album
        self.duration = song.duration
        self._on_play = on_play

        index_label = tk.Label(
            self, text=str(index + 1), fg="#999999", bg=bg,
            font=("Arial", 9, "bold" if is_current else "normal"), width=3
        )
        index_label.pack(side="left", padx=(8, 0))

        reorder_frame = tk.Frame(self, bg=bg)
        reorder_frame.pack(side="left", padx=(2, 0))
        up_btn = tk.Label(reorder_frame, text="▲", fg="#999999", bg=bg, cursor="hand2", font=("Arial", 8))
        up_btn.pack(side="top")
        up_btn.bind("<Button-1>", lambda e: on_move_up())
        down_btn = tk.Label(reorder_frame, text="▼", fg="#999999", bg=bg, cursor="hand2", font=("Arial", 8))
        down_btn.pack(side="top")
        down_btn.bind("<Button-1>", lambda e: on_move_down())

        info_frame = tk.Frame(self, bg=bg)
        info_frame.pack(side="left", fill="both", expand=True, padx=8)

        title_label = tk.Label(
            info_frame, text=f"{self.title} - {artists} / {self.album}",
            fg="#1abc9c" if is_current else "#ffffff", bg=bg,
            font=("Arial", 10, "bold"), anchor="w", cursor="hand2"
        )
        title_label.pack(fill="x", pady=(18, 0))
        title_label.bind("<Button-1>", lambda e: on_play())

        actions_frame = tk.Frame(self, bg=bg)
        actions_frame.pack(side="right", padx=8)

        minutes, seconds = divmod(self.duration, 60)
        duration_label = tk.Label(
            actions_frame, text=f"{minutes}:{seconds:02d}", fg="#999999", bg=bg, font=("Arial", 9)
        )
        duration_label.pack(side="left", padx=5)

        menu_image = load_image(BASE_DIR / "menu-dots-vertical.png", 20, 20)
        self.menu_btn = tk.Label(actions_frame, image=menu_image, bg=bg, cursor="hand2")
        self.menu_btn.image = menu_image
        self.menu_btn.pack(side="left", padx=5)
        self.menu_btn.bind("<Button-1>", self._show_menu)

        cross_image = load_image(BASE_DIR / "cross.png", 16, 16)
        remove_btn = tk.Label(actions_frame, image=cross_image, bg=bg, cursor="hand2")
        remove_btn.image = cross_image
        remove_btn.pack(side="left", padx=(5, 0))
        remove_btn.bind("<Button-1>", lambda e: on_remove())

    def _toggle_favori(self):
        from controllers.favori_controller import favori_controller
        if self.favori:
            favori_controller.remove_favori(self.id_song)
        else:
            favori_controller.add_favori(self.id_song)
        self.favori = not self.favori

    def _show_menu(self, event):
        # on_play_override : dans la file d'attente, "Lire" doit juste jouer
        # ce morceau, pas vider puis reconstruire la file avec lui seul.
        menu = build_song_context_menu(
            self, [self.id_song],
            favori_state=self.favori,
            on_toggle_favori=self._toggle_favori,
            play_label="Lire",
            on_play_override=self._on_play,
        )
        menu.tk_popup(event.x_root, event.y_root)


class QueueView(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color="#1e1e1e")
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # ===== HEADER =====
        header = ctk.CTkFrame(self, fg_color="#2c3e50", height=60)
        header.grid(row=0, column=0, sticky="ew")
        header.pack_propagate(False)

        ctk.CTkLabel(
            header, text="File d'attente", text_color="white", font=("Arial", 14, "bold")
        ).pack(side="left", padx=20, pady=10)

        self.position_btn = ctk.CTkButton(
            header, text="0 / 0", command=self._scroll_to_current,
            fg_color="transparent", hover_color="#34495e", text_color="#cccccc",
            width=80, height=28, font=("Arial", 11)
        )
        self.position_btn.pack(side="left", padx=10)

        self.duration_label = ctk.CTkLabel(
            header, text="0:00", text_color="#cccccc", font=("Arial", 11)
        )
        self.duration_label.pack(side="left", padx=5)

        clear_btn = ctk.CTkButton(
            header, text="Vider la file", command=self.clear_queue,
            fg_color="#e74c3c", hover_color="#c0392b", text_color="white", width=110
        )
        clear_btn.pack(side="right", padx=20, pady=10)

        # ===== CONTENU (scrollable) =====
        main_frame = tk.Frame(self, bg="#1e1e1e")
        main_frame.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)

        self.canvas = tk.Canvas(main_frame, bg="#1e1e1e", highlightthickness=0)
        self.canvas.pack(side="left", fill="both", expand=True)

        scrollbar = tk.Scrollbar(main_frame, orient="vertical", command=self.canvas.yview)
        scrollbar.pack(side="right", fill="y")
        self.canvas.configure(yscrollcommand=scrollbar.set)

        self.frame_content = tk.Frame(self.canvas, bg="#1e1e1e")
        self.content_window = self.canvas.create_window((0, 0), window=self.frame_content, anchor="nw")
        self.frame_content.bind(
            "<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        # Synchronise la largeur du contenu avec celle du canvas (sinon les
        # lignes gardent leur largeur "naturelle" minimale au lieu de
        # remplir l'espace disponible).
        self.canvas.bind(
            "<Configure>", lambda e: self.canvas.itemconfigure(self.content_window, width=e.width)
        )

        self._current_widget = None
        self.refresh()

    def refresh(self):
        """Recharge entièrement la file d'attente affichée. À appeler à
        chaque fois que la page devient visible ou après une action."""
        for child in self.frame_content.winfo_children():
            child.destroy()
        self._current_widget = None

        try:
            songs = library_controller.list_queue()
            status = player_controller.player_status()
            current_song = status.get("song")
            current_id = current_song.id if current_song else None

            total_duration = sum(s.duration for s in songs)
            minutes, seconds = divmod(total_duration, 60)
            self.duration_label.configure(text=f"{minutes}:{seconds:02d}")

            if not songs:
                self.position_btn.configure(text="0 / 0")
                empty_label = tk.Label(
                    self.frame_content, text="La file d'attente est vide",
                    fg="#999999", bg="#1e1e1e", font=("Arial", 12)
                )
                empty_label.pack(pady=50)
                return

            current_index = 0
            for i, song in enumerate(songs):
                is_current = song.id == current_id
                if is_current:
                    current_index = i
                row = QueueSongRow(
                    self.frame_content, i, song, is_current,
                    on_play=lambda sid=song.id: self._play(sid),
                    on_remove=lambda sid=song.id: self._remove(sid),
                    on_move_up=lambda idx=i: self._move(idx, idx - 1),
                    on_move_down=lambda idx=i: self._move(idx, idx + 1),
                )
                row.pack(fill="x", padx=5, pady=2)
                if is_current:
                    self._current_widget = row

            self.position_btn.configure(text=f"{current_index + 1} / {len(songs)}")

        except Exception as e:
            error_label = tk.Label(
                self.frame_content, text=f"Erreur: {str(e)}", fg="red", bg="#1e1e1e", font=("Arial", 11)
            )
            error_label.pack(pady=50)

    def _play(self, id_song):
        player_controller.play_song(id_song)
        self.refresh()

    def _remove(self, id_song):
        queue_controller.remove_song(id_song)
        self.refresh()

    def _move(self, pos_init, pos_target):
        songs = library_controller.list_queue()
        if pos_target < 0 or pos_target >= len(songs):
            return
        id_song = songs[pos_init].id
        queue_controller.move_song(id_song, pos_init, pos_target)
        self.refresh()

    def clear_queue(self):
        queue_controller.clear_queue()
        self.refresh()

    def _scroll_to_current(self):
        if self._current_widget is None:
            return
        self.update_idletasks()
        bbox = self.canvas.bbox("all")
        if not bbox:
            return
        total_height = bbox[3] - bbox[1]
        y = self._current_widget.winfo_y()
        if total_height > 0:
            self.canvas.yview_moveto(y / total_height)
