"""
Menu.py — CustomTkinter
Menu latéral (sidebar) rétractable avec sélection d'importation multiple.
"""
import sys
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

import customtkinter as ctk
from customtkinter import filedialog
from controllers.directory_controller import directory_controller
from PIL import Image

IMAGE_PATH = os.path.join(BASE_DIR, "asset", "file-dattente.png")
IMPORT_PATH = os.path.join(BASE_DIR, "asset", "image.png")

def load_white_icon(path, size=(20, 20)):
    img = Image.open(path).convert("RGBA")
    _, _, _, a = img.split()
    white_bg = Image.new("RGB", img.size, (255, 255, 255))
    white_img = Image.merge("RGBA", (*white_bg.split(), a))
    return ctk.CTkImage(light_image=white_img, dark_image=white_img, size=size)

img_queue = load_white_icon(IMAGE_PATH) if os.path.exists(IMAGE_PATH) else "\u2630"
img_import = load_white_icon(IMPORT_PATH) if os.path.exists(IMPORT_PATH) else "\u2913"

MENU_ITEMS = [
    ("\U0001F3E0", "Accueil"),
    ("\U0001F4BF", "Albums"),
    ("\U0001F3A4", "Artistes"),
    ("\U0001F3B5", "Morceaux"),
    ("\U0001F4CB", "Playlists"),
    (img_queue, "File d'attente"),
    ("\u2764", "Favoris"),
    ("\u2699", "Paramètres"),
    (img_import, "Import"),
]

class SideMenu(ctk.CTkFrame):
    def __init__(self, master, on_select=None, on_import_success=None, width_expanded=220, width_collapsed=0, **kwargs):
        super().__init__(master, width=width_expanded, corner_radius=0, fg_color="#0d0d0d", **kwargs)
        self.on_select = on_select
        self.on_import_success = on_import_success
        self.width_expanded = width_expanded
        self.width_collapsed = width_collapsed
        self.is_open = True
        self.buttons = {}

        self.pack_propagate(False)
        self._build_items()

    def _build_items(self):
        for icon, label in MENU_ITEMS:
            btn_kwargs = {
                "anchor": "w",
                "fg_color": "transparent",
                "hover_color": "#1f1f1f",
                "text_color": "#e0e0e0",
                "font": ctk.CTkFont(size=14),
                "height": 40,
                "command": lambda l=label: self._select(l),
            }
            if isinstance(icon, ctk.CTkImage):
                btn = ctk.CTkButton(self, text=f"   {label}", image=icon, compound="left", **btn_kwargs)
            else:
                btn = ctk.CTkButton(self, text=f"  {icon}   {label}", **btn_kwargs)

            btn.pack(fill="x", padx=8, pady=2)
            self.buttons[label] = btn

    def _select(self, label):
        for name, btn in self.buttons.items():
            btn.configure(
                fg_color="#1DB954" if name == label else "transparent",
                text_color="#000000" if name == label else "#e0e0e0"
            )

        if label == "Import":
            self._ouvrir_dialogue_import()
        elif self.on_select:
            self.on_select(label)

    def _ouvrir_dialogue_import(self):
        dialog = ctk.CTkToplevel(self)
        dialog.title("Importer de la musique")
        dialog.geometry("340x200")
        dialog.attributes("-topmost", True)
        dialog.configure(fg_color="#1f1f1f")

        label = ctk.CTkLabel(dialog, text="Que voulez-vous importer ?", font=ctk.CTkFont(size=14, weight="bold"))
        label.pack(pady=15)

        btn_dossier = ctk.CTkButton(
            dialog,
            text="Importer un dossier / Album(s)",
            fg_color="#1DB954",
            hover_color="#17a34a",
            command=lambda: [dialog.destroy(), self._importer_dossier()]
        )
        btn_dossier.pack(pady=5, fill="x", padx=20)

        btn_fichier = ctk.CTkButton(
            dialog,
            text="Importer un ou plusieurs morceau(x)",
            fg_color="#333333",
            hover_color="#444444",
            command=lambda: [dialog.destroy(), self._importer_fichiers()]
        )
        btn_fichier.pack(pady=5, fill="x", padx=20)

    def _importer_dossier(self):
        chemin = filedialog.askdirectory(title="Sélectionner le dossier racine ou l'album")
        if chemin:
            directory_controller.add(chemin)
            if self.on_import_success:
                self.on_import_success("Albums")
            
    def _importer_fichiers(self):
        chemins = filedialog.askopenfilenames(
            title="Sélectionner un ou plusieurs morceaux",
            filetypes=[("Fichiers audio", "*.mp3 *.wav *.flac *.ogg *.m4a")]
        )
        if chemins:
            dossiers_parents = {os.path.dirname(c) for c in chemins}
            for dossier in dossiers_parents:
                directory_controller.add(dossier)
                
            if self.on_import_success:
                self.on_import_success("Morceaux")

    def toggle(self):
        if self.is_open:
            self.configure(width=self.width_collapsed)
            self.pack_forget()
        else:
            self.configure(width=self.width_expanded)
            self.pack(side="left", fill="y")
        self.is_open = not self.is_open