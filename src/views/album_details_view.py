import tkinter as tk
from tkinter import messagebox
from models.album_model import Album
from models.song_model import Song
from views.song_list_item import SongListItem
from controllers.library_controller import library_controller
from controllers.player_controller import player_controller
from utils.function import load_image
from utils.constante import BASE_DIR

class AlbumDetailsView(tk.Frame):
    """View for displaying album details and songs"""
    def __init__(self, master, album: Album, on_back_callback=None):
        super().__init__(master, bg="#1e1e1e")
        
        self.album = album
        self.on_back_callback = on_back_callback
        self.selected_items = {}
        
        # ===== TOP BAR WITH BACK BUTTON =====
        top_bar = tk.Frame(self, bg="#2c3e50", height=60)
        top_bar.pack(side="top", fill="x")
        top_bar.pack_propagate(False)
        
        back_btn = tk.Button(
            top_bar,
            text="← Retour",
            command=self.go_back,
            bg="#34495e",
            fg="white"
        )
        back_btn.pack(side="left", padx=10, pady=10)
        
        title_label = tk.Label(
            top_bar,
            text=f"Album: {self.album.title}",
            fg="white",
            bg="#2c3e50",
            font=("Arial", 14, "bold")
        )
        title_label.pack(side="left", padx=20, pady=10)
        
        # ===== ALBUM HEADER =====
        header_frame = tk.Frame(self, bg="#2d2d2d", height=180)
        header_frame.pack(side="top", fill="x")
        header_frame.pack_propagate(False)
        
        # Album cover
        cover_path = self.album.cover_path if self.album.cover_path else BASE_DIR / "melodia_ia.png"
        cover_image = load_image(cover_path, 150, 150)
        cover_label = tk.Label(header_frame, image=cover_image, bg="#2d2d2d")
        cover_label.image = cover_image
        cover_label.pack(side="left", padx=20, pady=15)
        
        # Album info
        info_frame = tk.Frame(header_frame, bg="#2d2d2d")
        info_frame.pack(side="left", fill="both", expand=True, padx=20)
        
        album_title = tk.Label(
            info_frame,
            text=self.album.title,
            fg="white",
            bg="#2d2d2d",
            font=("Arial", 16, "bold"),
            anchor="w"
        )
        album_title.pack(fill="x", pady=(10, 5))
        
        artist_label = tk.Label(
            info_frame,
            text=f"Artiste: {self.album.artists}",
            fg="#999999",
            bg="#2d2d2d",
            font=("Arial", 11),
            anchor="w"
        )
        artist_label.pack(fill="x", pady=2)
        
        year_label = tk.Label(
            info_frame,
            text=f"Année: {self.album.release_year}",
            fg="#999999",
            bg="#2d2d2d",
            font=("Arial", 11),
            anchor="w"
        )
        year_label.pack(fill="x", pady=2)
        
        # ===== ACTION BAR (for selected items) =====
        self.action_bar = tk.Frame(self, bg="#3d3d3d", height=40)
        self.action_bar.pack_propagate(False)
        
        self.action_label = tk.Label(self.action_bar, text="", fg="white", bg="#3d3d3d")
        self.action_label.pack(side="left", padx=10, pady=5)
        
        self.action_btn_play = tk.Button(self.action_bar, text="Lire", command=self.play_selected)
        self.action_btn_play.pack(side="left", padx=5)
        
        self.action_btn_queue = tk.Button(self.action_bar, text="File d'attente", command=self.add_to_queue)
        self.action_btn_queue.pack(side="left", padx=5)
        
        self.action_btn_clear = tk.Button(self.action_bar, text="Effacer sélection", command=self.clear_selection)
        self.action_btn_clear.pack(side="left", padx=5)
        
        # ===== SONGS LIST =====
        main_frame = tk.Frame(self, bg="#1e1e1e")
        main_frame.pack(side="top", fill="both", expand=True)
        
        # Canvas with scroll
        canvas = tk.Canvas(
            main_frame,
            bg="#1e1e1e",
            highlightthickness=0
        )
        canvas.pack(side="left", fill="both", expand=True)
        
        scrollbar = tk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        scrollbar.pack(side="right", fill="y")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        self.frame_content = tk.Frame(canvas, bg="#1e1e1e")
        canvas.create_window((0, 0), window=self.frame_content, anchor="nw")
        self.frame_content.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        
        # Load songs from album
        songs = library_controller.list_songs_album(self.album.id)
        
        for song in songs:
            item = SongListItem(
                self.frame_content,
                song=song,
                on_click_callback=self._handle_song_selection,
                on_play_callback=self.play_song
            )
            item.pack(fill="x", padx=5, pady=2)
    
    def _handle_song_selection(self, song_id, widget):
        """Handle song selection"""
        if widget not in self.selected_items:
            self.selected_items[widget] = song_id
            widget.toggle_selection()
        else:
            del self.selected_items[widget]
            widget.toggle_selection()
        
        self.update_action_bar()
    
    def update_action_bar(self):
        """Show/hide action bar based on selection"""
        if self.selected_items:
            self.action_label.configure(text=f"{len(self.selected_items)} morceaux sélectionné(s)")
            self.action_bar.pack(side="top", fill="x")
        else:
            self.action_bar.pack_forget()
    
    def play_selected(self):
        """Play selected songs"""
        if self.selected_items:
            messagebox.showinfo("Lecture", f"Lecture de {len(self.selected_items)} morceau(x)")
        self.clear_selection()
    
    def add_to_queue(self):
        """Add selected songs to queue"""
        if self.selected_items:
            messagebox.showinfo("File d'attente", f"Ajout de {len(self.selected_items)} morceau(x) à la file")
        self.clear_selection()
    
    def clear_selection(self):
        """Clear all selections"""
        for widget in self.selected_items.keys():
            if hasattr(widget, 'toggle_selection'):
                widget.toggle_selection()
        
        self.selected_items.clear()
        self.action_bar.pack_forget()
    
    def play_song(self, song_id):
        """Play a single song"""
        player_controller.play_song(song_id)
        messagebox.showinfo("Lecture", f"Lecture du morceau")
    
    def go_back(self):
        """Go back to previous view"""
        if self.on_back_callback:
            self.on_back_callback()
