"""
Melodia-IA - Fenêtre d'édition des paroles (LyricsEditorDialog)
Architecture MVC - Boîte de dialogue modale ouverte depuis LyricsView.

Permet d'importer un fichier .lrc existant, de saisir/éditer le texte
brut des paroles d'un morceau, ou de générer automatiquement la
synchronisation (IA, via analyse audio) à partir de paroles non
synchronisées, puis de l'enregistrer réellement via le backend
(controllers/lyrics_controller -> services/lyrics_service ->
infrastructure/lyrics_manager).
"""

import threading
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
        self._has_existing_lyrics = False

        self.title(f"Paroles - {song.title}")
        self.geometry("520x560")
        self.minsize(420, 400)
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
                "existant, tapez/collez le texte brut ci-dessous, ou générez la "
                "synchronisation automatiquement (IA) à partir de paroles brutes."
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
            text_color=("gray40", "#A0A0B0"), anchor="w", justify="left", wraplength=480
        )
        self.lbl_status.pack(anchor="w", fill="x", padx=16)

        # Ligne d'actions liées aux paroles (import / synchro IA)
        sync_frame = ctk.CTkFrame(self, fg_color="transparent")
        sync_frame.pack(fill="x", padx=16, pady=(6, 0))

        self.btn_import = ctk.CTkButton(
            sync_frame, text="Importer un fichier .lrc", command=self.on_import_clicked
        )
        self.btn_import.pack(side="left")

        self.btn_auto_sync = ctk.CTkButton(
            sync_frame, text="⚡ Synchroniser automatiquement (IA)",
            fg_color=("#1f538d", "#1DB954"), hover_color=("#14375e", "#1ED760"),
            command=self.on_auto_sync_clicked
        )
        self.btn_auto_sync.pack(side="left", padx=(8, 0))

        # Ligne d'actions générales (retirer / annuler / enregistrer)
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(fill="x", padx=16, pady=(6, 16))

        self.btn_remove = ctk.CTkButton(
            btn_frame, text="Retirer les paroles",
            fg_color="transparent", border_width=1,
            text_color=("#b00020", "#FF6B6B"),
            hover_color=("gray85", "#1F1F28"),
            command=self.on_remove_clicked
        )
        self.btn_remove.pack(side="left")

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
            self._has_existing_lyrics = True
            self.btn_remove.configure(state="normal")
        else:
            self._has_existing_lyrics = False
            self.btn_remove.configure(state="disabled")

    def on_remove_clicked(self):
        lyrics_controller.remove_lyrics(self.song.id)
        self.textbox.delete("1.0", "end")
        self._has_existing_lyrics = False
        self.lbl_status.configure(text="Paroles retirées pour ce morceau.")
        if self.on_saved:
            self.on_saved()
        self.destroy()

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

    def on_auto_sync_clicked(self):
        """Lance la génération automatique de la synchronisation (IA) à
        partir du texte brut actuellement présent dans le champ de saisie.
        L'analyse audio (librosa) peut prendre quelques secondes : elle est
        exécutée dans un thread séparé pour ne pas geler l'interface, et le
        résultat est réinjecté dans le textbox une fois prêt.
        """
        raw_text = self.textbox.get("1.0", "end")
        lines = [line.strip() for line in raw_text.splitlines() if line.strip()]

        if not lines:
            self.lbl_status.configure(text="Rien à synchroniser : le champ de paroles est vide.")
            return

        self._set_controls_state("disabled")
        self.lbl_status.configure(text="Analyse audio en cours, veuillez patienter...")

        thread = threading.Thread(target=self._run_auto_sync, args=(lines,), daemon=True)
        thread.start()

    def _run_auto_sync(self, lines):
        # Exécuté hors du thread principal Tk : ne touche à aucun widget ici,
        # on se contente d'appeler le backend puis de replanifier la mise à
        # jour de l'UI sur le thread principal via `after`.
        try:
            result = lyrics_controller.generate_automatic_sync(self.song.id, lines)
        except Exception as e:
            result = False
            print(f"[LyricsEditorDialog] Erreur synchronisation automatique: {e}")
        self.after(0, self._on_auto_sync_done, result)

    def _on_auto_sync_done(self, result):
        self._set_controls_state("normal")

        if not result:
            self.lbl_status.configure(
                text="Échec de la synchronisation automatique "
                     "(audio introuvable ou illisible)."
            )
            return

        self.textbox.delete("1.0", "end")
        self.textbox.insert("1.0", "\n".join(result))
        self.lbl_status.configure(
            text=f"Synchronisation automatique générée pour {len(result)} ligne(s). "
                 "Vérifiez le résultat puis cliquez sur \"Enregistrer\"."
        )

    def _set_controls_state(self, state):
        self.btn_import.configure(state=state)
        self.btn_auto_sync.configure(state=state)
        self.btn_save.configure(state=state)
        if state == "normal":
            self.btn_remove.configure(state="normal" if self._has_existing_lyrics else "disabled")
        else:
            self.btn_remove.configure(state="disabled")

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
