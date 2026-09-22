import tkinter as tk
from utils.function import load_image
from utils.constante import BASE_DIR
from models.song_model import Song

class SongListItem(tk.Frame):
    """Composant pour afficher une chanson en liste"""
    def __init__(self, parent, song: Song, on_click_callback=None, on_play_callback=None):
        super().__init__(parent, bg="#2d2d2d", height=60)
        self.pack_propagate(False)
        
        self.id_song = song.id
        self.title = song.title
        self.artists = ", ".join(song.artists) if isinstance(song.artists, list) else song.artists
        self.album = song.album
        self.duration = song.duration
        self.selected = False
        self.on_click_callback = on_click_callback
        self.on_play_callback = on_play_callback
        
        # Layout horizontal avec cover, infos et boutons
        # Cover
        cover_path = song.cover_path if song.cover_path else BASE_DIR / "melodia_ia.png"
        cover_image = load_image(cover_path, 50, 50)
        self.cover_label = tk.Label(self, image=cover_image, bg="#2d2d2d")
        self.cover_label.image = cover_image
        self.cover_label.pack(side="left", padx=10, pady=5)
        self.cover_label.bind("<Button-1>", self._on_click)
        
        # Infos
        info_frame = tk.Frame(self, bg="#2d2d2d")
        info_frame.pack(side="left", fill="both", expand=True, padx=5)
        
        self.title_label = tk.Label(
            info_frame,
            text=self.title,
            fg="#ffffff",
            bg="#2d2d2d",
            font=("Arial", 11, "bold"),
            anchor="w"
        )
        self.title_label.pack(fill="x")
        self.title_label.bind("<Button-1>", self._on_click)
        
        self.artist_label = tk.Label(
            info_frame,
            text=self.artists,
            fg="#999999",
            bg="#2d2d2d",
            font=("Arial", 9),
            anchor="w"
        )
        self.artist_label.pack(fill="x")
        self.artist_label.bind("<Button-1>", self._on_click)
        
        # Actions frame
        actions_frame = tk.Frame(self, bg="#2d2d2d")
        actions_frame.pack(side="right", padx=10)
        
        # Duration
        minutes = self.duration // 60
        seconds = self.duration % 60
        self.duration_label = tk.Label(
            actions_frame,
            text=f"{minutes}:{seconds:02d}",
            fg="#999999",
            bg="#2d2d2d",
            font=("Arial", 9)
        )
        self.duration_label.pack(side="left", padx=5)
        self.duration_label.bind("<Button-1>", self._on_click)
        
        # Menu button
        menu_image = load_image(BASE_DIR / "menu-dots-vertical.png", 24, 24)
        self.menu_btn = tk.Label(
            actions_frame,
            image=menu_image,
            bg="#2d2d2d",
            cursor="hand2"
        )
        self.menu_btn.image = menu_image
        self.menu_btn.pack(side="left", padx=5)
        self.menu_btn.bind("<Button-1>", self.show_options_menu)
        
        # Bind click event for selection
        self.bind("<Button-1>", self._on_click)
        
    def _on_click(self, event=None):
        """Toggle selection on click"""
        if self.on_click_callback:
            self.on_click_callback(self.id_song, self)
    
    def toggle_selection(self):
        """Toggle selection state"""
        self.selected = not self.selected
        if self.selected:
            self.configure(bg="#3d3d3d")
            self.cover_label.configure(bg="#3d3d3d")
            info_frame = self.winfo_children()[1]
            info_frame.configure(bg="#3d3d3d")
            for child in info_frame.winfo_children():
                if isinstance(child, tk.Label):
                    child.configure(bg="#3d3d3d")
            actions_frame = self.winfo_children()[2]
            actions_frame.configure(bg="#3d3d3d")
            for child in actions_frame.winfo_children():
                if isinstance(child, tk.Label):
                    child.configure(bg="#3d3d3d")
        else:
            self.configure(bg="#2d2d2d")
            self.cover_label.configure(bg="#2d2d2d")
            info_frame = self.winfo_children()[1]
            info_frame.configure(bg="#2d2d2d")
            for child in info_frame.winfo_children():
                if isinstance(child, tk.Label):
                    child.configure(bg="#2d2d2d")
            actions_frame = self.winfo_children()[2]
            actions_frame.configure(bg="#2d2d2d")
            for child in actions_frame.winfo_children():
                if isinstance(child, tk.Label):
                    child.configure(bg="#2d2d2d")
    
    def show_options_menu(self, event):
        """Show context menu for the song"""
        menu = tk.Menu(self, tearoff=0, bg="#2d2d2d", fg="white", activebackground="#4a4a4a")
        menu.add_command(label="Lire", command=lambda: self._play_song())
        menu.add_command(label="Ajouter à la file d'attente", command=lambda: print(f"Ajouté à la file: {self.title}"))
        menu.add_command(label="Ajouter aux favoris", command=lambda: print(f"Ajouté aux favoris: {self.title}"))
        menu.add_separator()
        menu.add_command(label="Supprimer", command=lambda: print(f"Supprimé: {self.title}"))
        
        menu.post(event.x_root, event.y_root)
    
    def _play_song(self):
        """Play the song"""
        if self.on_play_callback:
            self.on_play_callback(self.id_song)
