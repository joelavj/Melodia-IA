"""
Melodia-IA - Fenêtre d'édition des paroles (LyricsEditorDialog)
Architecture MVC - Boîte de dialogue modale ouverte depuis LyricsView.

Permet d'importer un fichier .lrc existant ou de saisir/éditer le texte
brut des paroles d'un morceau, puis de l'enregistrer réellement via le
backend (controllers/lyrics_controller -> services/lyrics_service ->
infrastructure/lyrics_manager).
"""

from tkinter import filedialog

try:
    import customtkinter as ctk
    USE_CTK = True
except ImportError:
    import tkinter as ctk
    USE_CTK = False

from controllers.lyrics_controller import lyrics_controller

BASE_TOPLEVEL = ctk.CTkToplevel if USE_CTK else ctk.Toplevel


class LyricsEditorDialog(BASE_TOPLEVEL):
    def __init__(self, parent, song, on_saved=None):
        super().__init__(parent)
        self.song = song
        self.on_saved = on_saved

        self.title(f"Paroles - {song.title}")
        self.geometry("520x520")
        self.minsize(420, 360)
        # Fenêtre modale : bloque l'interaction avec le reste de l'appli
        # tant qu'elle n'est pas fermée (édition/import en cours).
        self.transient(parent)
        self.after(50, self.grab_set)

        self._setup_ui()
        self._load_existing_lyrics()

    def _setup_ui(self):
        artists = ", ".join(self.song.artists) if self.song.artists else "Artiste inconnu"
        header = ctk.CTkLabel(
            self,
            text=f"{self.song.title} — {artists}",
            font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),
            anchor="w"
        )
        header.pack(anchor="w", fill="x", padx=16, pady=(16, 4))

        hint = ctk.CTkLabel(
            self,
            text=(
                "Une ligne de parole par ligne de texte. Importez un fichier .lrc "
                "existant ou tapez/collez le texte brut ci-dessous."
            ),
            font=ctk.CTkFont(family="Segoe UI", size=11),
            text_color=("gray40", "#A0A0B0"),
            anchor="w",
            justify="left",
            wraplength=480
        )
        hint.pack(anchor="w", fill="x", padx=16, pady=(0, 10))

        self.textbox = ctk.CTkTextbox(self, font=ctk.CTkFont(family="Segoe UI", size=13))
        self.textbox.pack(fill="both", expand=True, padx=16, pady=(0, 10))

        self.lbl_status = ctk.CTkLabel(
            self, text="", font=ctk.CTkFont(family="Segoe UI", size=11),
            text_color=("gray40", "#A0A0B0"), anchor="w"
        )
        self.lbl_status.pack(anchor="w", fill="x", padx=16)

        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(fill="x", padx=16, pady=(6, 16))

        self.btn_import = ctk.CTkButton(
            btn_frame, text="Importer un fichier .lrc", command=self.on_import_clicked
        )
        self.btn_import.pack(side="left")

        self.btn_cancel = ctk.CTkButton(
            btn_frame, text="Annuler", fg_color="transparent", border_width=1,
            text_color=("gray20", "#EAEAEA"),
            command=self.destroy
        )
        self.btn_cancel.pack(side="right", padx=(8, 0))

        self.btn_save = ctk.CTkButton(
            btn_frame, text="Enregistrer",
            fg_color=("#1f538d", "#1DB954"), hover_color=("#14375e", "#1ED760"),
            command=self.on_save_clicked
        )
        self.btn_save.pack(side="right")

    def _load_existing_lyrics(self):
        existing = lyrics_controller.get_lyrics(self.song.id)
        if existing:
            content = "\n".join(line.rstrip("\n") for line in existing)
            self.textbox.insert("1.0", content)

    def on_import_clicked(self):
        path = filedialog.askopenfilename(
            parent=self,
            title="Importer un fichier de paroles",
            filetypes=[("Fichier LRC", "*.lrc"), ("Tous les fichiers", "*.*")]
        )
        if not path:
            return
        imported = lyrics_controller.import_lyrics_file(path)
        if not imported:
            self.lbl_status.configure(text="Le fichier importé ne contient aucune ligne exploitable.")
            return
        self.textbox.delete("1.0", "end")
        self.textbox.insert("1.0", "\n".join(imported))
        self.lbl_status.configure(text=f"{len(imported)} ligne(s) importée(s) depuis {path.split('/')[-1]}.")

    def on_save_clicked(self):
        raw_text = self.textbox.get("1.0", "end")
        lines = raw_text.splitlines()
        cleaned_lines = lyrics_controller.edit_lyrics(None, lines)

        if not cleaned_lines:
            self.lbl_status.configure(text="Rien à enregistrer : le champ de paroles est vide.")
            return

        lyrics_controller.save_lyrics(self.song.id, cleaned_lines)

        if self.on_saved:
            self.on_saved()
        self.destroy()
