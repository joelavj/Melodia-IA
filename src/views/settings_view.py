import customtkinter as ctk
from tkinter import messagebox


class SettingsView(ctk.CTkFrame):
    """View for application settings"""
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
            text="Paramètres",
            text_color="white",
            font=("Arial", 14, "bold")
        )
        title_label.pack(side="left", padx=20, pady=10)
        
        # ===== CONTENT =====
        content = ctk.CTkScrollableFrame(self, fg_color="#1e1e1e")
        content.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
        content.grid_columnconfigure(0, weight=1)
        
        # ===== APPEARANCE SECTION =====
        appearance_label = ctk.CTkLabel(
            content,
            text="Apparence",
            text_color="white",
            font=("Arial", 12, "bold")
        )
        appearance_label.pack(fill="x", padx=20, pady=(20, 10))
        
        # Theme selection
        theme_frame = ctk.CTkFrame(content, fg_color="#2d2d2d", corner_radius=5)
        theme_frame.pack(fill="x", padx=20, pady=5)
        
        theme_label = ctk.CTkLabel(
            theme_frame,
            text="Thème:",
            text_color="white",
            font=("Arial", 11)
        )
        theme_label.pack(side="left", padx=10, pady=10)
        
        theme_var = ctk.StringVar(value="dark")
        dark_radio = ctk.CTkRadioButton(
            theme_frame,
            text="Sombre",
            variable=theme_var,
            value="dark",
            text_color="white"
        )
        dark_radio.pack(side="left", padx=10)
        
        light_radio = ctk.CTkRadioButton(
            theme_frame,
            text="Clair",
            variable=theme_var,
            value="light",
            text_color="white"
        )
        light_radio.pack(side="left", padx=10)
        
        # ===== AUDIO SECTION =====
        audio_label = ctk.CTkLabel(
            content,
            text="Audio",
            text_color="white",
            font=("Arial", 12, "bold")
        )
        audio_label.pack(fill="x", padx=20, pady=(20, 10))
        
        # Volume
        volume_frame = ctk.CTkFrame(content, fg_color="#2d2d2d", corner_radius=5)
        volume_frame.pack(fill="x", padx=20, pady=5)
        
        volume_label = ctk.CTkLabel(
            volume_frame,
            text="Volume:",
            text_color="white",
            font=("Arial", 11)
        )
        volume_label.pack(side="left", padx=10, pady=10)
        
        volume_slider = ctk.CTkSlider(
            volume_frame,
            from_=0,
            to=100,
            fg_color="#34495e"
        )
        volume_slider.set(80)
        volume_slider.pack(side="left", fill="x", expand=True, padx=10, pady=10)
        
        # ===== PLAYBACK SECTION =====
        playback_label = ctk.CTkLabel(
            content,
            text="Lecture",
            text_color="white",
            font=("Arial", 12, "bold")
        )
        playback_label.pack(fill="x", padx=20, pady=(20, 10))
        
        repeat_frame = ctk.CTkFrame(content, fg_color="#2d2d2d", corner_radius=5)
        repeat_frame.pack(fill="x", padx=20, pady=5)
        
        repeat_label = ctk.CTkLabel(
            repeat_frame,
            text="Répétition:",
            text_color="white",
            font=("Arial", 11)
        )
        repeat_label.pack(side="left", padx=10, pady=10)
        
        repeat_var = ctk.StringVar(value="off")
        off_radio = ctk.CTkRadioButton(
            repeat_frame,
            text="Arrêt",
            variable=repeat_var,
            value="off",
            text_color="white"
        )
        off_radio.pack(side="left", padx=10)
        
        one_radio = ctk.CTkRadioButton(
            repeat_frame,
            text="Une fois",
            variable=repeat_var,
            value="one",
            text_color="white"
        )
        one_radio.pack(side="left", padx=10)
        
        all_radio = ctk.CTkRadioButton(
            repeat_frame,
            text="Tous",
            variable=repeat_var,
            value="all",
            text_color="white"
        )
        all_radio.pack(side="left", padx=10)
        
        # Shuffle
        shuffle_check = ctk.CTkCheckBox(
            content,
            text="Mélanger la lecture",
            text_color="white",
            checkmark_color="#1abc9c",
            border_color="#34495e",
            fg_color="#34495e"
        )
        shuffle_check.pack(fill="x", padx=20, pady=10)
        
        # ===== SAVE BUTTON =====
        save_btn = ctk.CTkButton(
            content,
            text="Sauvegarder les paramètres",
            command=self.save_settings,
            fg_color="#1abc9c",
            text_color="white",
            height=40,
            font=("Arial", 12)
        )
        save_btn.pack(fill="x", padx=20, pady=20)
    
    def save_settings(self):
        """Save settings"""
        messagebox.showinfo("Succès", "Paramètres sauvegardés avec succès!")
