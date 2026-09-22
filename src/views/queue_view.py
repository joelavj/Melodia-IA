import customtkinter as ctk
from controllers.library_controller import library_controller
from controllers.queue_controller import queue_controller
from controllers.player_controller import player_controller


class QueueView(ctk.CTkFrame):
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
            text="File d'attente",
            text_color="white",
            font=("Arial", 14, "bold")
        )
        title_label.pack(side="left", padx=20, pady=10)
        
        clear_btn = ctk.CTkButton(
            header,
            text="Vider",
            command=self.clear_queue,
            fg_color="#e74c3c",
            text_color="white",
            width=100
        )
        clear_btn.pack(side="right", padx=20, pady=10)
        
        # ===== CONTENT =====
        content = ctk.CTkScrollableFrame(self, fg_color="#1e1e1e")
        content.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
        content.grid_columnconfigure(0, weight=1)
        
        # Load queue
        try:
            queue_songs = library_controller.list_queue()
            
            if not queue_songs:
                empty_label = ctk.CTkLabel(
                    content,
                    text="La file d'attente est vide",
                    text_color="gray",
                    font=("Arial", 12)
                )
                empty_label.pack(pady=50)
            else:
                for i, song in enumerate(queue_songs):
                    song_frame = ctk.CTkFrame(content, fg_color="#2d2d2d", corner_radius=5)
                    song_frame.pack(fill="x", padx=5, pady=3)
                    
                    song_label = ctk.CTkLabel(
                        song_frame,
                        text=f"{i+1}. {song.title}",
                        text_color="white",
                        font=("Arial", 11)
                    )
                    song_label.pack(fill="x", padx=10, pady=8)
        
        except Exception as e:
            error_label = ctk.CTkLabel(
                content,
                text=f"Erreur: {str(e)}",
                text_color="red",
                font=("Arial", 11)
            )
            error_label.pack(pady=50)
    
    def clear_queue(self):
        """Clear the queue"""
        queue_controller.clear_queue()
        # Refresh would be needed here
