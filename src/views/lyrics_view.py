import tkinter as tk
from tkinter import messagebox, filedialog
from controllers.lyrics_controller import lyrics_controller
from controllers.player_controller import player_controller

class LyricsView(tk.Frame):
    """View for displaying song lyrics"""
    def __init__(self, master, on_back_callback=None):
        super().__init__(master, bg="#1e1e1e")
        
        self.on_back_callback = on_back_callback
        self.current_song = None
        self.lyrics_lines = []
        self.current_lyric_index = 0
        
        # ===== HEADER =====
        header = tk.Frame(self, bg="#2c3e50", height=50)
        header.pack(side="top", fill="x")
        header.pack_propagate(False)
        
        back_btn = tk.Button(
            header,
            text="← Retour",
            command=self.go_back,
            bg="#34495e",
            fg="white"
        )
        back_btn.pack(side="left", padx=10, pady=10)
        
        self.title_label = tk.Label(
            header,
            text="Paroles",
            fg="white",
            bg="#2c3e50",
            font=("Arial", 14, "bold")
        )
        self.title_label.pack(side="left", padx=20, pady=10)
        
        # Export button
        export_btn = tk.Button(
            header,
            text="Exporter LRC",
            command=self.export_lyrics,
            bg="#3498db",
            fg="white"
        )
        export_btn.pack(side="right", padx=10, pady=10)
        
        # Generate sync button
        generate_btn = tk.Button(
            header,
            text="Générer sync",
            command=self.generate_sync,
            bg="#1abc9c",
            fg="white"
        )
        generate_btn.pack(side="right", padx=10, pady=10)
        
        # ===== MAIN LYRICS DISPLAY =====
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
        
        self.lyrics_frame = tk.Frame(canvas, bg="#1e1e1e")
        self._canvas = canvas
        canvas.create_window((0, 0), window=self.lyrics_frame, anchor="nw")
        self.lyrics_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        
        self.refresh_lyrics()
    
    def refresh_lyrics(self):
        """Refresh lyrics display"""
        # Clear current lyrics
        for child in self.lyrics_frame.winfo_children():
            child.destroy()
        
        # Get current song
        try:
            status = player_controller.player_status()
            current_song = status.get("song")
            
            if not current_song:
                empty_label = tk.Label(
                    self.lyrics_frame,
                    text="Aucun morceau en cours de lecture",
                    fg="gray",
                    bg="#1e1e1e",
                    font=("Arial", 12)
                )
                empty_label.pack(pady=50)
                return
            
            self.current_song = current_song
            
            # Get lyrics
            lyrics = lyrics_controller.get_lyrics(current_song.id)
            
            if not lyrics:
                no_lyrics_label = tk.Label(
                    self.lyrics_frame,
                    text="Aucune parole disponible pour ce morceau",
                    fg="gray",
                    bg="#1e1e1e",
                    font=("Arial", 12)
                )
                no_lyrics_label.pack(pady=50)
                return
            
            # Parse lyrics (assuming format: [00:00]Lyric line or plain text)
            self.lyrics_lines = self._parse_lyrics(lyrics)
            
            # Display lyrics
            for i, (timestamp, text) in enumerate(self.lyrics_lines):
                line_frame = tk.Frame(self.lyrics_frame, bg="#1e1e1e")
                line_frame.pack(fill="x", padx=20, pady=5)
                
                # Timestamp (if synchronized)
                if timestamp:
                    time_label = tk.Label(
                        line_frame,
                        text=timestamp,
                        fg="#666666",
                        bg="#1e1e1e",
                        font=("Arial", 8),
                        width=8
                    )
                    time_label.pack(side="left", padx=5)
                
                # Lyric text
                text_label = tk.Label(
                    line_frame,
                    text=text,
                    fg="#ffffff",
                    bg="#1e1e1e",
                    font=("Arial", 12),
                    anchor="w",
                    wraplength=600,
                    justify="left"
                )
                text_label.pack(side="left", fill="x", expand=True)
                
                # Store widget for highlighting later
                text_label.line_index = i
        
        except Exception as e:
            error_label = tk.Label(
                self.lyrics_frame,
                text=f"Erreur: {str(e)}",
                fg="red",
                bg="#1e1e1e",
                font=("Arial", 10)
            )
            error_label.pack(pady=50)
    
    def _parse_lyrics(self, lyrics_text):
        """Parse lyrics text and extract timestamps and text"""
        lines = []
        
        for line in lyrics_text.strip().split('\n'):
            # Check for LRC format [mm:ss]
            if line.startswith('[') and ']' in line:
                bracket_pos = line.index(']')
                timestamp = line[1:bracket_pos]
                text = line[bracket_pos + 1:].strip()
                lines.append((timestamp, text))
            else:
                # Plain text line
                lines.append((None, line.strip()))
        
        return lines
    
    def export_lyrics(self):
        """Export lyrics to LRC file"""
        if not self.current_song:
            messagebox.showwarning("Export", "Aucun morceau disponible")
            return
        
        file_path = filedialog.asksaveasfilename(
            defaultextension=".lrc",
            filetypes=[("LRC files", "*.lrc"), ("Text files", "*.txt")]
        )
        
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    for timestamp, text in self.lyrics_lines:
                        if timestamp:
                            f.write(f"[{timestamp}]{text}\n")
                        else:
                            f.write(f"{text}\n")
                
                messagebox.showinfo("Export", "Paroles exportées avec succès!")
            except Exception as e:
                messagebox.showerror("Erreur", f"Erreur lors de l'export: {str(e)}")
    
    def generate_sync(self):
        """Generate synchronization for lyrics"""
        if not self.current_song:
            messagebox.showwarning("Sync", "Aucun morceau disponible")
            return
        
        messagebox.showinfo(
            "Synchronisation",
            "Cliquez sur une ligne de parole quand elle est chantée pour synchroniser.\nCette fonctionnalité sera implémentée."
        )
        # TODO: Implement interactive sync generation
    
    def go_back(self):
        """Go back to previous view"""
        if self.on_back_callback:
            self.on_back_callback()
