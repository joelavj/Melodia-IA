import customtkinter as ctk
from controllers.library_controller import library_controller


class PlaylistsView(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color="#1e1e1e")
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        # ===== HEADER =====
        header = ctk.CTkFrame(self, fg_color="#2c3e50", height=60)
        header.grid(row=0, column=0, sticky="ew")
        header.pack_propagate(False)
        
        title_label = ctk.CTkLabel(
            header,
            text="Playlists",
            text_color="white",
            font=("Arial", 14, "bold")
        )
        title_label.pack(side="left", padx=20, pady=10)
        
        create_btn = ctk.CTkButton(
            header,
            text="+ Créer",
            fg_color="#1abc9c",
            text_color="white",
            width=100
        )
        create_btn.pack(side="right", padx=20, pady=10)
        
        # ===== CONTENT =====
        content = ctk.CTkScrollableFrame(self, fg_color="#1e1e1e")
        content.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
        content.grid_columnconfigure(0, weight=1)
        
        # Load playlists
        try:
            playlists = library_controller.list_playlists()
            
            if not playlists:
                empty_label = ctk.CTkLabel(
                    content,
                    text="Aucune playlist créée",
                    text_color="gray",
                    font=("Arial", 12)
                )
                empty_label.pack(pady=50)
            else:
                for playlist in playlists:
                    pl_frame = ctk.CTkFrame(content, fg_color="#2d2d2d", corner_radius=5)
                    pl_frame.pack(fill="x", padx=5, pady=3)
                    
                    pl_label = ctk.CTkLabel(
                        pl_frame,
                        text=playlist.name,
                        text_color="white",
                        font=("Arial", 11)
                    )
                    pl_label.pack(fill="x", padx=10, pady=8)
        
        except Exception as e:
            error_label = ctk.CTkLabel(
                content,
                text=f"Erreur: {str(e)}",
                text_color="red",
                font=("Arial", 11)
            )
            error_label.pack(pady=50)
