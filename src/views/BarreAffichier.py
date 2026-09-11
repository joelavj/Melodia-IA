"""
BarreAffichier.py — CustomTkinter
Panneau latéral droit : affichage des paroles du morceau en cours et
barre de notation (étoiles) de la chanson.
"""

import customtkinter as ctk

DUMMY_LYRICS = """Miverina indray aho
Any amin'ny lalako
Ny fitiavana no tadiaviko
Ho hitako any an-dàlana

(Refrain)
Miverina, miverina
Any amin'ny fahazavana
"""


class LyricsPanel(ctk.CTkFrame):
    """Panneau d'affichage des paroles + notation de la chanson en cours."""

    def __init__(self, master, on_rate=None, width=280, **kwargs):
        super().__init__(master, width=width, corner_radius=0, fg_color="#0d0d0d", **kwargs)
        self.on_rate = on_rate
        self.rating = 0
        self.star_buttons = []

        self.pack_propagate(False)

        ctk.CTkLabel(self, text="Paroles", font=ctk.CTkFont(size=16, weight="bold")).pack(
            anchor="w", padx=16, pady=(16, 4)
        )

        self.txt_lyrics = ctk.CTkTextbox(self, wrap="word", fg_color="#181818", corner_radius=8)
        self.txt_lyrics.pack(fill="both", expand=True, padx=16, pady=(0, 16))
        self.txt_lyrics.insert("1.0", DUMMY_LYRICS)
        self.txt_lyrics.configure(state="disabled")

        ctk.CTkLabel(self, text="Note de la chanson", font=ctk.CTkFont(size=13)).pack(
            anchor="w", padx=16
        )

        stars_frame = ctk.CTkFrame(self,fg_color="#181818", corner_radius=8)
        stars_frame.pack(fill="both", expand=True, padx=16,pady=(0, 16))
        noteSon = ctk.CTkLabel(stars_frame, text="afficher ici le note de la chanson", font=ctk.CTkFont(size=13))
        noteSon.pack(side="left", ipadx=10, ipady=5)       


    def _set_rating(self, note):
        self.rating = note
        for i, btn in enumerate(self.star_buttons, start=1):
            btn.configure(text="\u2605" if i <= note else "\u2606")
        if self.on_rate:
            self.on_rate(note)

    def set_lyrics(self, texte):
        self.txt_lyrics.configure(state="normal")
        self.txt_lyrics.delete("1.0", "end")
        self.txt_lyrics.insert("1.0", texte)
        self.txt_lyrics.configure(state="disabled")


if __name__ == "__main__":
    app = ctk.CTk()
    app.geometry("320x600")
    panel = LyricsPanel(app, on_rate=lambda n: print("note:", n))
    panel.pack(fill="both", expand=True)
    app.mainloop()
