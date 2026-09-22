import customtkinter as ctk
from controllers.player_controller import player_controller


class PlayerBar(ctk.CTkFrame):
    """Bottom player control bar"""
    def __init__(self, master):
        super().__init__(master, fg_color="#26BADF", height=100, corner_radius=0)
        self.pack_propagate(False)
        
        # ===== LEFT SIDE: INFO =====
        left_frame = ctk.CTkFrame(self, fg_color="#26BADF")
        left_frame.pack(side="left", fill="y", padx=10, pady=10)
        
        title_label = ctk.CTkLabel(
            left_frame,
            text="Aucun morceau",
            text_color="white",
            font=("Arial", 11, "bold")
        )
        title_label.pack()
        
        artist_label = ctk.CTkLabel(
            left_frame,
            text="",
            text_color="white",
            font=("Arial", 9)
        )
        artist_label.pack()
        
        # ===== CENTER: PLAYBACK CONTROLS =====
        center_frame = ctk.CTkFrame(self, fg_color="#26BADF")
        center_frame.pack(side="left", fill="both", expand=True, padx=20)
        
        button_frame = ctk.CTkFrame(center_frame, fg_color="#26BADF")
        button_frame.pack(pady=10)
        
        prev_btn = ctk.CTkButton(
            button_frame,
            text="⏮ Précédent",
            command=self.previous_track,
            fg_color="#34495e",
            text_color="white",
            width=100,
            height=35,
            font=("Arial", 10)
        )
        prev_btn.pack(side="left", padx=5)
        
        play_btn = ctk.CTkButton(
            button_frame,
            text="▶ Lire",
            command=self.toggle_play,
            fg_color="#1abc9c",
            text_color="white",
            width=100,
            height=35,
            font=("Arial", 10, "bold")
        )
        play_btn.pack(side="left", padx=5)
        
        next_btn = ctk.CTkButton(
            button_frame,
            text="Suivant ⏭",
            command=self.next_track,
            fg_color="#34495e",
            text_color="white",
            width=100,
            height=35,
            font=("Arial", 10)
        )
        next_btn.pack(side="left", padx=5)
        
        # Progress bar
        progress_frame = ctk.CTkFrame(center_frame, fg_color="#26BADF")
        progress_frame.pack(fill="x", pady=5)
        
        time_label = ctk.CTkLabel(progress_frame, text="0:00", text_color="white", font=("Arial", 9))
        time_label.pack(side="left", padx=5)
        
        progress_slider = ctk.CTkSlider(
            progress_frame,
            from_=0,
            to=100,
            orient="horizontal",
            fg_color="#34495e"
        )
        progress_slider.pack(side="left", fill="x", expand=True, padx=5)
        
        duration_label = ctk.CTkLabel(progress_frame, text="0:00", text_color="white", font=("Arial", 9))
        duration_label.pack(side="left", padx=5)
        
        # ===== RIGHT SIDE: VOLUME =====
        right_frame = ctk.CTkFrame(self, fg_color="#26BADF")
        right_frame.pack(side="right", fill="y", padx=10, pady=10)
        
        volume_label = ctk.CTkLabel(
            right_frame,
            text="Volume:",
            text_color="white",
            font=("Arial", 10)
        )
        volume_label.pack(pady=5)
        
        volume_slider = ctk.CTkSlider(
            right_frame,
            from_=0,
            to=100,
            orient="vertical",
            height=60,
            fg_color="#34495e"
        )
        volume_slider.set(80)
        volume_slider.pack(pady=5)
    
    def toggle_play(self):
        """Toggle play/pause"""
        player_controller.play_song()
    
    def next_track(self):
        """Play next track"""
        player_controller.next_song()
    
    def previous_track(self):
        """Play previous track"""
        player_controller.previous_song()
