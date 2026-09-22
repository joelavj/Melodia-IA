import customtkinter as ctk
from controllers.library_controller import library_controller
from controllers.player_controller import player_controller


class Acceuil(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color="#1e1e1e")
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        self.current_tab = "Album"
        self.selected_items = {}
        self.scroll_positions = {}
        
        # ===== TOP BAR =====
        top_bar = ctk.CTkFrame(self, fg_color="#2c3e50", height=60)
        top_bar.grid(row=0, column=0, sticky="ew", padx=0, pady=0)
        top_bar.grid_propagate(False)
        top_bar.grid_columnconfigure(0, weight=0)  # Tabs (left)
        top_bar.grid_columnconfigure(1, weight=1)  # Empty space
        top_bar.grid_columnconfigure(2, weight=0)  # Search (right)
        
        # Left side: Tab buttons
        tabs_frame = ctk.CTkFrame(top_bar, fg_color="#2c3e50")
        tabs_frame.grid(row=0, column=0, sticky="w", padx=10, pady=10)
        
        self.boutons = {}
        self.boutons["Album"] = ctk.CTkButton(
            tabs_frame,
            text="Album",
            command=lambda: self.changer_onglet("Album"),
            fg_color="#1abc9c",
            text_color="white",
            width=100,
            height=35,
            font=("Arial", 12)
        )
        self.boutons["Album"].grid(row=0, column=0, padx=5)
        
        self.boutons["Artiste"] = ctk.CTkButton(
            tabs_frame,
            text="Artiste",
            command=lambda: self.changer_onglet("Artiste"),
            fg_color="#34495e",
            text_color="white",
            width=100,
            height=35,
            font=("Arial", 12)
        )
        self.boutons["Artiste"].grid(row=0, column=1, padx=5)
        
        self.boutons["Morceau"] = ctk.CTkButton(
            tabs_frame,
            text="Morceau",
            command=lambda: self.changer_onglet("Morceau"),
            fg_color="#34495e",
            text_color="white",
            width=100,
            height=35,
            font=("Arial", 12)
        )
        self.boutons["Morceau"].grid(row=0, column=2, padx=5)
        
        # Right side: Search bar
        search_frame = ctk.CTkFrame(top_bar, fg_color="#2c3e50")
        search_frame.grid(row=0, column=2, sticky="e", padx=10, pady=10)
        
        search_label = ctk.CTkLabel(
            search_frame,
            text="Rechercher:",
            text_color="white",
            font=("Arial", 11)
        )
        search_label.pack(side="left", padx=5)
        
        self.search_var = ctk.StringVar()
        self.search_var.trace("w", lambda name, index, mode: self.search_content())
        self.search_entry = ctk.CTkEntry(
            search_frame,
            textvariable=self.search_var,
            placeholder_text="Rechercher...",
            width=250,
            height=35,
            font=("Arial", 11)
        )
        self.search_entry.pack(side="left", padx=5)
        
        # ===== ACTION BAR (for selected items) =====
        self.action_bar = ctk.CTkFrame(self, fg_color="#3d3d3d", height=40)
        # Not packed initially
        
        # ===== CONTENT AREA =====
        content_frame = ctk.CTkFrame(self, fg_color="#1e1e1e")
        content_frame.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
        content_frame.grid_rowconfigure(0, weight=1)
        content_frame.grid_columnconfigure(0, weight=1)
        
        # Create scrollable frame
        self.scrollable_frame = ctk.CTkScrollableFrame(
            content_frame,
            fg_color="#1e1e1e",
            label_text=""
        )
        self.scrollable_frame.grid(row=0, column=0, sticky="nsew")
        self.scrollable_frame.grid_columnconfigure(0, weight=1)
        
        self.frame_content = self.scrollable_frame
        
        # Display albums by default
        self.afficher_albums()
    
    def changer_onglet(self, nom_onglet: str):
        """Change the current tab"""
        self.search_var.set("")  # Clear search
        self.clear_selection()
        
        # Update button colors
        for nom, btn in self.boutons.items():
            btn.configure(fg_color="#34495e")
        
        self.boutons[nom_onglet].configure(fg_color="#1abc9c")
        
        # Clear content
        for child in self.frame_content.winfo_children():
            child.destroy()
        
        # Update current tab
        self.current_tab = nom_onglet
        
        # Load appropriate tab
        if nom_onglet == "Album":
            self.afficher_albums()
        elif nom_onglet == "Artiste":
            self.afficher_artistes()
        elif nom_onglet == "Morceau":
            self.afficher_morceaux()
    
    def afficher_albums(self):
        """Display albums as cards"""
        try:
            albums = library_controller.list_albums()
            
            if not albums:
                empty_label = ctk.CTkLabel(
                    self.frame_content,
                    text="Aucun album disponible. Ajoutez un répertoire dans les paramètres.",
                    text_color="gray",
                    font=("Arial", 12)
                )
                empty_label.pack(pady=50)
                return
            
            # Create grid layout
            for i, album in enumerate(albums):
                album_frame = ctk.CTkFrame(
                    self.frame_content,
                    fg_color="#2d2d2d",
                    corner_radius=10
                )
                album_frame.pack(fill="x", padx=10, pady=5)
                
                # Album card with cover and info
                info_label = ctk.CTkLabel(
                    album_frame,
                    text=f"{album.title} - {album.artists}",
                    text_color="white",
                    font=("Arial", 11),
                    wraplength=400
                )
                info_label.pack(fill="x", padx=10, pady=10)
        
        except Exception as e:
            error_label = ctk.CTkLabel(
                self.frame_content,
                text=f"Erreur: {str(e)}",
                text_color="red",
                font=("Arial", 11)
            )
            error_label.pack(pady=50)
    
    def afficher_artistes(self):
        """Display artists as list"""
        try:
            artists = library_controller.list_artists()
            
            if not artists:
                empty_label = ctk.CTkLabel(
                    self.frame_content,
                    text="Aucun artiste disponible",
                    text_color="gray",
                    font=("Arial", 12)
                )
                empty_label.pack(pady=50)
                return
            
            for artist in artists:
                artist_frame = ctk.CTkFrame(
                    self.frame_content,
                    fg_color="#2d2d2d",
                    corner_radius=5
                )
                artist_frame.pack(fill="x", padx=10, pady=5)
                
                name_label = ctk.CTkLabel(
                    artist_frame,
                    text=artist.name,
                    text_color="white",
                    font=("Arial", 11)
                )
                name_label.pack(fill="x", padx=10, pady=10)
        
        except Exception as e:
            error_label = ctk.CTkLabel(
                self.frame_content,
                text=f"Erreur: {str(e)}",
                text_color="red",
                font=("Arial", 11)
            )
            error_label.pack(pady=50)
    
    def afficher_morceaux(self):
        """Display songs as list"""
        try:
            songs = library_controller.list_songs()
            
            if not songs:
                empty_label = ctk.CTkLabel(
                    self.frame_content,
                    text="Aucun morceau disponible",
                    text_color="gray",
                    font=("Arial", 12)
                )
                empty_label.pack(pady=50)
                return
            
            for song in songs:
                song_frame = ctk.CTkFrame(
                    self.frame_content,
                    fg_color="#2d2d2d",
                    corner_radius=5
                )
                song_frame.pack(fill="x", padx=10, pady=5)
                
                title_label = ctk.CTkLabel(
                    song_frame,
                    text=f"{song.title} - {', '.join(song.artists) if isinstance(song.artists, list) else song.artists}",
                    text_color="white",
                    font=("Arial", 11)
                )
                title_label.pack(fill="x", padx=10, pady=10)
        
        except Exception as e:
            error_label = ctk.CTkLabel(
                self.frame_content,
                text=f"Erreur: {str(e)}",
                text_color="red",
                font=("Arial", 11)
            )
            error_label.pack(pady=50)
    
    def search_content(self):
        """Search in current tab"""
        search_term = self.search_var.get().lower()
        
        if not search_term:
            self.changer_onglet(self.current_tab)
            return
        
        # Clear content
        for child in self.frame_content.winfo_children():
            child.destroy()
        
        try:
            if self.current_tab == "Album":
                albums = library_controller.list_albums()
                filtered = [a for a in albums if search_term in a.title.lower()]
                
                if not filtered:
                    empty_label = ctk.CTkLabel(
                        self.frame_content,
                        text="Aucun album trouvé",
                        text_color="gray"
                    )
                    empty_label.pack(pady=50)
                else:
                    for album in filtered:
                        frame = ctk.CTkFrame(self.frame_content, fg_color="#2d2d2d")
                        frame.pack(fill="x", padx=10, pady=5)
                        label = ctk.CTkLabel(frame, text=f"{album.title} - {album.artists}", text_color="white")
                        label.pack(fill="x", padx=10, pady=10)
        
        except Exception as e:
            error_label = ctk.CTkLabel(
                self.frame_content,
                text=f"Erreur: {str(e)}",
                text_color="red"
            )
            error_label.pack(pady=50)
    
    def clear_selection(self):
        """Clear all selections"""
        self.selected_items.clear()
        self.action_bar.grid_forget()
