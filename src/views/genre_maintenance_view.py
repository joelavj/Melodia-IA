"""Panneau d'entretien de la bibliothèque : détection automatique du genre
pour tous les morceaux qui n'en ont pas.

Composant autonome (CTkFrame), pensé pour être posé dans la page où ce
type d'action globale de fond a le plus de sens dans l'appli — par
exemple à côté de "Scanner tous les répertoires" dans la section
Répertoire, ou dans Paramètres.

Intégration (2 lignes) dans la vue qui l'accueille :
    from views.genre_maintenance_view import GenreMaintenanceView
    ...
    GenreMaintenanceView(parent).pack(fill="x", padx=10, pady=10)
"""

import customtkinter as ctk
from controllers.ai_controller import ai_controller


class GenreMaintenanceView(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color="#2d2d2d", corner_radius=8)

        ctk.CTkLabel(
            self, text="Détection automatique du genre",
            text_color="white", font=("Arial", 12, "bold")
        ).pack(anchor="w", padx=15, pady=(10, 0))

        ctk.CTkLabel(
            self,
            text="Analyse le contenu audio des morceaux sans genre renseigné. "
                 "Peut prendre du temps selon le nombre de morceaux : "
                 "l'application reste utilisable pendant l'opération.",
            text_color="#999999", font=("Arial", 10), wraplength=500, justify="left"
        ).pack(anchor="w", padx=15, pady=(0, 10))

        bottom = ctk.CTkFrame(self, fg_color="transparent")
        bottom.pack(fill="x", padx=15, pady=(0, 15))

        self.status_var = ctk.StringVar(value="")
        ctk.CTkLabel(bottom, textvariable=self.status_var, text_color="#1abc9c").pack(side="left")

        self.launch_btn = ctk.CTkButton(
            bottom, text="Détecter les genres manquants",
            command=self._lancer_detection, fg_color="#1abc9c", text_color="white"
        )
        self.launch_btn.pack(side="right")

    def _lancer_detection(self):
        self.launch_btn.configure(state="disabled")
        self.status_var.set("Démarrage...")

        def _on_progress(done, total):
            if not self.winfo_exists():
                return
            self.status_var.set(f"Analyse en cours... {done}/{total}")

        def _on_done(results):
            if not self.winfo_exists():
                return
            n = len(results)
            self.status_var.set(f"{n} genre(s) détecté(s)." if n else "Aucun genre détecté (ou rien à traiter).")
            self.launch_btn.configure(state="normal")

        ai_controller.detect_missing_genres_async(_on_done, on_progress=_on_progress, widget=self)