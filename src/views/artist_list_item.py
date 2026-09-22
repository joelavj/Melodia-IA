import tkinter as tk
from utils.function import load_image
from utils.constante import BASE_DIR
from models.artist_model import Artist

class ArtistListItem(tk.Frame):
    """Composant pour afficher un artiste en liste"""
    def __init__(self, parent, artist: Artist, on_click_callback=None):
        super().__init__(parent, bg="#2d2d2d", height=60)
        self.pack_propagate(False)
        
        self.id_artist = artist.id
        self.name = artist.name
        self.album_count = getattr(artist, 'album_count', 0)
        self.song_count = getattr(artist, 'song_count', 0)
        self.selected = False
        self.on_click_callback = on_click_callback
        
        # Bind click event for selection
        self.bind("<Button-1>", self._on_click)
        
        # Avatar/cover
        cover_path = getattr(artist, 'cover_path', None)
        cover_path = cover_path if cover_path else BASE_DIR / "melodia_ia.png"
        cover_image = load_image(cover_path, 50, 50)
        self.cover_label = tk.Label(self, image=cover_image, bg="#2d2d2d")
        self.cover_label.image = cover_image
        self.cover_label.pack(side="left", padx=10, pady=5)
        self.cover_label.bind("<Button-1>", self._on_click)
        
        # Infos
        info_frame = tk.Frame(self, bg="#2d2d2d")
        info_frame.pack(side="left", fill="both", expand=True, padx=5)
        
        self.name_label = tk.Label(
            info_frame,
            text=self.name,
            fg="#ffffff",
            bg="#2d2d2d",
            font=("Arial", 11, "bold"),
            anchor="w"
        )
        self.name_label.pack(fill="x")
        self.name_label.bind("<Button-1>", self._on_click)
        
        count_text = f"{self.album_count} albums • {self.song_count} morceaux"
        self.count_label = tk.Label(
            info_frame,
            text=count_text,
            fg="#999999",
            bg="#2d2d2d",
            font=("Arial", 9),
            anchor="w"
        )
        self.count_label.pack(fill="x")
        self.count_label.bind("<Button-1>", self._on_click)
        
        # Menu button
        menu_image = load_image(BASE_DIR / "menu-dots-vertical.png", 24, 24)
        self.menu_btn = tk.Label(
            self,
            image=menu_image,
            bg="#2d2d2d",
            cursor="hand2"
        )
        self.menu_btn.image = menu_image
        self.menu_btn.pack(side="right", padx=10)
        self.menu_btn.bind("<Button-1>", self.show_options_menu)
    
    def _on_click(self, event=None):
        """Handle click event"""
        if self.on_click_callback:
            self.on_click_callback(self.id_artist, self)
    
    def toggle_selection(self):
        """Toggle selection state"""
        self.selected = not self.selected
        if self.selected:
            self.configure(bg="#3d3d3d")
            for child in self.winfo_children():
                if isinstance(child, tk.Label):
                    child.configure(bg="#3d3d3d")
        else:
            self.configure(bg="#2d2d2d")
            for child in self.winfo_children():
                if isinstance(child, tk.Label):
                    child.configure(bg="#2d2d2d")
    
    def show_options_menu(self, event):
        """Show context menu for the artist"""
        menu = tk.Menu(self, tearoff=0, bg="#2d2d2d", fg="white", activebackground="#4a4a4a")
        menu.add_command(label="Lire tous les morceaux", command=lambda: print(f"Lecture de {self.name}"))
        menu.add_command(label="Ajouter à la file d'attente", command=lambda: print(f"Ajouté à la file: {self.name}"))
        menu.add_separator()
        menu.add_command(label="Supprimer", command=lambda: print(f"Supprimé: {self.name}"))
        
        menu.post(event.x_root, event.y_root)
