import tkinter as tk
from utils.function import load_image
from utils.constante import BASE_DIR
from models.album_model import Album

class AlbumCard(tk.Frame):
    def __init__(self,parent, album:Album, on_click_callback=None):
        super().__init__(parent, bd=2, relief="groove", bg="#1e1e1e", width=150, height=220)
        self.pack_propagate(False)
        
        self.id_album = album.id
        self.title = album.title
        self.artists = album.artists
        self.release_year = album.release_year
        self.selected = False
        self.on_click_callback = on_click_callback

        # Pochette de l'album
        cover_path = album.cover_path if album.cover_path is not None else BASE_DIR / "melodia_ia.png"
        cover_image = load_image(cover_path, 130, 130)
        self.cover = tk.Label(self, image=cover_image, bg="#1e1e1e", cursor="hand2")
        self.cover.image = cover_image
        self.cover.pack(side="top", fill="x", padx=10, pady=(10, 5))
        self.cover.bind("<Button-1>", lambda event: self.toogle_selection(event))

        # Zone du bas avec titre et artiste
        self.bottom_frame = tk.Frame(self, bg="#1E1E1E")
        self.bottom_frame.pack(side="bottom", fill="both", expand=True, padx=5, pady=5)

        # Titre de l'album
        self.title_label = tk.Label(
            self.bottom_frame,
            text=self.title,
            fg="white",
            bg="#1e1e1e",
            font=("Arial", 10, "bold"),
            anchor="nw",
            justify="left",
            wraplength=130
        )
        self.title_label.pack(fill="x", anchor="nw")
        self.title_label.bind("<Button-1>", lambda e: self.open_content())

        # Artiste
        self.artist_label = tk.Label(
            self.bottom_frame,
            text=self.artists,
            fg="#999999",
            bg="#1e1e1e",
            font=("Arial", 8),
            anchor="nw",
            justify="left",
            wraplength=130
        )
        self.artist_label.pack(fill="x", anchor="nw")
        self.artist_label.bind("<Button-1>", lambda e: self.open_content())

        # Bouton trois points verticaux
        icone_menu = load_image(BASE_DIR / "menu-dots-vertical.png", 20, 20)
        menu_frame = tk.Frame(self.bottom_frame, bg="#1e1e1e")
        menu_frame.pack(fill="x")
        
        self.options_btn = tk.Label(
            menu_frame,
            image=icone_menu,
            bg="#1e1e1e",
            cursor="hand2"
        )
        self.options_btn.image = icone_menu
        self.options_btn.pack(side="right")
        self.options_btn.bind("<Button-1>", self.show_options_menu)

    def toogle_selection(self, event=None):
        """Toggle selection state"""
        self.selected = not self.selected
        if self.selected:
            self.config(relief="solid", bd=2, bg="#2d2d2d")
            self.bottom_frame.config(bg="#2d2d2d")
            self.cover.config(bg="#2d2d2d")
            self.title_label.config(bg="#2d2d2d")
            self.artist_label.config(bg="#2d2d2d")
            self.options_btn.config(bg="#2d2d2d")
        else:
            self.config(relief="groove", bd=2, bg="#1e1e1e")
            self.bottom_frame.config(bg="#1e1e1e")
            self.cover.config(bg="#1e1e1e")
            self.title_label.config(bg="#1e1e1e")
            self.artist_label.config(bg="#1e1e1e")
            self.options_btn.config(bg="#1e1e1e")

    def open_content(self):
        """Open album details"""
        if self.on_click_callback:
            self.on_click_callback(self.title)

    def show_options_menu(self, event):
        """Show context menu"""
        menu = tk.Menu(self, tearoff=0, bg="#2d2d2d", fg="white", activebackground="#4a4a4a")
        menu.add_command(label="Lire l'album", command=lambda: print(f"Lecture de : {self.title}"))
        menu.add_command(label="Ajouter à la file d'attente", command=lambda: print(f"Ajouté : {self.title}"))
        menu.add_separator()
        menu.add_command(label="Supprimer", command=lambda: print(f"Supprimé : {self.title}"))

        menu.post(event.x_root, event.y_root)