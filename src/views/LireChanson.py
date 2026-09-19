"""
LireChanson.py — CustomTkinter
Barre de lecture en bas de l'application : pochette, titre/artiste, contrôles
(précédent, play/pause, suivant, stop, répéter), volume et barre de progression
avec temps de début / temps de fin.
"""
import sys
import os
import time

# Ajout du dossier parent au système de fichiers pour importer les contrôleurs correctement
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Importation du contrôleur audio principal et des bibliothèques GUI
from controllers.player_controller import player_controller as pc
import customtkinter as ctk
from PIL import Image


class PlayerBar(ctk.CTkFrame):
    """Barre de lecture interactive affichant le morceau en cours et ses contrôles."""

    # Temps de pause (en secondes) évitant que la boucle automatique n'écrase le curseur lors d'un déplacement manuel
    DELAI_APRES_SEEK_MANUEL = 0.6
    # Fréquence de rafraîchissement de l'interface graphique (en millisecondes)
    INTERVALLE_BOUCLE_MS = 500

    def __init__(self, master, on_play_pause=None, on_next=None, on_prev=None,
                 on_volume_change=None, on_seek=None, on_toggle_lyrics=None, **kwargs):
        """Initialise la barre de lecture, ses sous-composants et ses callbacks."""
        super().__init__(master, height=90, corner_radius=0, fg_color="#181818", **kwargs)
        
        # Sauvegarde des fonctions de rappel (callbacks)
        self.on_play_pause = on_play_pause
        self.on_next = on_next
        self.on_prev = on_prev
        self.on_volume_change = on_volume_change
        self.on_seek = on_seek
        self.on_toggle_lyrics = on_toggle_lyrics

        # État interne du lecteur
        self.is_playing = False
        self._cover_label = None
        self._duree = 0.0
        self._dernier_seek_manuel = 0.0
        self._loop_id = None

        # Configuration de la grille Tkinter
        self.pack_propagate(False)
        self.grid_columnconfigure(1, weight=1)

        # ==========================================
        # SECTION GAUCHE : Pochette & Informations
        # ==========================================
        left = ctk.CTkFrame(self, fg_color="transparent")
        left.grid(row=0, column=0, sticky="w", padx=16, pady=10)

        # Conteneur pour la pochette de l'album/morceau
        self.cover = ctk.CTkFrame(left, fg_color="#1DB954", width=56, height=56, corner_radius=6)
        self.cover.pack(side="left")
        self.cover.pack_propagate(False)

        # Labels pour le titre et l'artiste
        info = ctk.CTkFrame(left, fg_color="transparent")
        info.pack(side="left", padx=10)
        self.lbl_titre = ctk.CTkLabel(info, text="Aucun morceau", font=ctk.CTkFont(size=13, weight="bold"))
        self.lbl_titre.pack(anchor="w")
        self.lbl_artiste = ctk.CTkLabel(info, text="—", font=ctk.CTkFont(size=11), text_color="#a0a0a0")
        self.lbl_artiste.pack(anchor="w")

        # ==========================================
        # SECTION CENTRALE : Contrôles & Progression
        # ==========================================
        center = ctk.CTkFrame(self, fg_color="transparent")
        center.grid(row=0, column=1, sticky="ew", pady=10)
        center.grid_columnconfigure(0, weight=1)

        # Boutons de lecture
        controls = ctk.CTkFrame(center, fg_color="transparent")
        controls.pack()

        # Bouton Répéter
        self.btn_repeat = ctk.CTkButton(controls, text="\U0001F502", width=32, height=32,
                                         fg_color="transparent", hover_color="#282828",
                                         text_color="#a0a0a0",
                                         font=ctk.CTkFont(size=14), command=self._repeat)
        self.btn_repeat.pack(side="left", padx=6)

        # Bouton Précédent
        self.btn_prev = ctk.CTkButton(controls, text="\u23EE", width=36, height=36,
                                       fg_color="transparent", hover_color="#282828",
                                       font=ctk.CTkFont(size=16), command=self._prev)
        self.btn_prev.pack(side="left", padx=6)

        # Bouton Lecture / Pause
        self.btn_play = ctk.CTkButton(controls, text="\u25B6", width=42, height=42,
                                       corner_radius=21, fg_color="#1DB954",
                                       hover_color="#17a34a", text_color="#000000",
                                       font=ctk.CTkFont(size=16), command=self._play_pause)
        self.btn_play.pack(side="left", padx=6)

        # Bouton Suivant
        self.btn_next = ctk.CTkButton(controls, text="\u23ED", width=36, height=36,
                                       fg_color="transparent", hover_color="#282828",
                                       font=ctk.CTkFont(size=16), command=self._next)
        self.btn_next.pack(side="left", padx=6)

        # Bouton Stop
        self.btn_stop = ctk.CTkButton(controls, text="\u23F9", width=32, height=32,
                                       fg_color="transparent", hover_color="#282828",
                                       font=ctk.CTkFont(size=14), command=self._stop)
        self.btn_stop.pack(side="left", padx=6)

        # Barre de défilement temporel (Slider)
        progress_row = ctk.CTkFrame(center, fg_color="transparent")
        progress_row.pack(fill="x", padx=20, pady=(8, 0))
        progress_row.grid_columnconfigure(1, weight=1)

        # Temps écoulé
        self.lbl_temps_debut = ctk.CTkLabel(progress_row, text="00:00",
                                             font=ctk.CTkFont(size=10), text_color="#a0a0a0")
        self.lbl_temps_debut.grid(row=0, column=0, padx=(0, 8))

        # Curseur de progression
        self.progress = ctk.CTkSlider(progress_row, from_=0, to=100, command=self._seek)
        self.progress.set(0)
        self.progress.grid(row=0, column=1, sticky="ew")

        # Durée totale
        self.lbl_temps_fin = ctk.CTkLabel(progress_row, text="00:00",
                                           font=ctk.CTkFont(size=10), text_color="#a0a0a0")
        self.lbl_temps_fin.grid(row=0, column=2, padx=(8, 0))

        # ==========================================
        # SECTION DROITE : Paroles & Volume
        # ==========================================
        right = ctk.CTkFrame(self, fg_color="transparent")
        right.grid(row=0, column=2, sticky="e", padx=16)

        # Bouton pour afficher/masquer les paroles
        self.btn_lyrics = ctk.CTkButton(right, text="\U0001F3A4", width=32, height=32,
                                         fg_color="transparent", hover_color="#282828",
                                         font=ctk.CTkFont(size=14), command=self._toggle_lyrics)
        self.btn_lyrics.pack(side="left", padx=(0, 10))

        # Icône dynamique de volume
        self.lbl_volume = ctk.CTkLabel(right, text="\U0001F50A", font=ctk.CTkFont(size=14))
        self.lbl_volume.pack(side="left", padx=(0, 6))

        # Slider de réglage du volume
        self.volume = ctk.CTkSlider(
            right, from_=0, to=100, width=100, command=self.mettre_a_jour_volume
        )
        self.volume.set(70)
        self.volume.pack(side="left")

        # Démarrage de la mise à jour automatique
        self.demarrer_boucle()

    # --- Utilitaires de conversion et gestion du temps ---

    def _formater_temps(self, secondes) -> str:
        """Convertit des secondes en format lisible mm:ss (ex: 125 -> 02:05)."""
        try:
            secondes = int(max(0, float(secondes)))
        except (TypeError, ValueError):
            secondes = 0
        return f"{secondes // 60:02d}:{secondes % 60:02d}"

    def _obtenir_duree(self, song) -> float:
        """Extrait la durée d'un morceau de manière sécurisée quel que soit l'attribut du modèle."""
        if song is None:
            return 0.0
        duree = (
            getattr(song, "duration", None)
            or getattr(song, "duree", None)
            or getattr(song, "length", None)
            or 0
        )
        try:
            return float(duree)
        except (TypeError, ValueError):
            return 0.0

    def _reinitialiser_progression(self):
        """Réinitialise l'affichage de la barre de progression et des compteurs de temps."""
        self._duree = 0.0
        self.progress.configure(to=100)
        self.progress.set(0)
        self.lbl_temps_debut.configure(text="00:00")
        self.lbl_temps_fin.configure(text="00:00")

    # --- Boucle de synchronisation de l'interface ---

    def _lire_position_courante(self) -> float:
        """Récupère la position temporelle courante auprès du contrôleur audio."""
        try:
            return float(pc.current_position())
        except (TypeError, ValueError, AttributeError):
            return 0.0

    def _boucle_lecture(self):
        """
        Boucle d'actualisation appelée périodiquement :
        - Traite les événements audio
        - Met à jour la barre de progression
        - Bascule automatiquement vers la chanson suivante en fin de morceau
        """
        try:
            pc.process_event()
            status = pc.player_status()
            song = status.get("song")
            is_playing = bool(status.get("is_playing", False))

            # Mise à jour des bornes du slider si le morceau a changé
            duree = self._obtenir_duree(song)
            if duree != self._duree:
                self._duree = duree
                self.progress.configure(to=duree if duree > 0 else 100)
                self.lbl_temps_fin.configure(text=self._formater_temps(duree))

            # Mise à jour de la position courante si aucun déplacement manuel récent n'a eu lieu
            if (time.time() - self._dernier_seek_manuel) > self.DELAI_APRES_SEEK_MANUEL:
                temps_debut = self._lire_position_courante()

                # Fin de chanson atteinte -> passage au morceau suivant
                if self._duree > 0 and temps_debut >= self._duree:
                    pc.next_song()
                    self._reinitialiser_progression()
                    self.update_status()
                else:
                    self.progress.set(temps_debut)
                    self.lbl_temps_debut.configure(text=self._formater_temps(temps_debut))

            # Ajustement de l'icône du bouton play/pause
            self.is_playing = is_playing
            self.btn_play.configure(text="\u23F8" if is_playing else "\u25B6")
        except Exception as e:
            print(f"[PlayerBar] Erreur boucle_lecture: {e}")
        finally:
            # Planifie la prochaine exécution de la boucle
            self._loop_id = self.after(self.INTERVALLE_BOUCLE_MS, self._boucle_lecture)

    def demarrer_boucle(self):
        """Lance la boucle de synchronisation de l'UI."""
        if self._loop_id is None:
            self._boucle_lecture()

    def arreter_boucle(self):
        """Arrête proprement la boucle de synchronisation (ex: lors de la fermeture de l'application)."""
        if self._loop_id is not None:
            self.after_cancel(self._loop_id)
            self._loop_id = None

    # --- Actions utilisateur & Interaction avec le PlayerController ---

    def update_status(self):
        """Met à jour l'affichage de la barre avec les informations du morceau en cours."""
        try:
            status = pc.player_status()
            song = status.get("song")
            is_playing = bool(status.get("is_playing", False))

            if song:
                titre = getattr(song, 'title', None) or getattr(song, 'name', None) or os.path.basename(getattr(song, 'path', '')) or "Titre inconnu"
                artiste = getattr(song, 'artist', None) or getattr(song, 'artist_name', 'Artiste inconnu')
                cover_path = getattr(song, 'cover_path', None)
                self.set_song(titre, artiste, cover_path)

            self.is_playing = is_playing
            self.btn_play.configure(text="\u23F8" if is_playing else "\u25B6")
        except Exception as e:
            print(f"[PlayerBar] Erreur update_status: {e}")

    def jouer_morceau(self, id_song: int):
        """Déclenche la lecture d'un morceau donné via son identifiant."""
        pc.play_song(id_song=id_song)
        self.update_status()

    def _play_pause(self):
        """Bascule le lecteur entre Lecture et Pause."""
        pc.play_song()
        self.update_status()
        if self.on_play_pause:
            self.on_play_pause(self.is_playing)

    def _next(self):
        """Passe au morceau suivant dans la liste."""
        pc.next_song()
        self._reinitialiser_progression()
        self.update_status()
        if self.on_next:
            self.on_next()

    def _prev(self):
        """Revient au morceau précédent."""
        pc.previous_song()
        self._reinitialiser_progression()
        self.update_status()
        if self.on_prev:
            self.on_prev()

    def _stop(self):
        """Arrête complètement la lecture."""
        pc.stop_play()
        self._reinitialiser_progression()
        self.is_playing = False
        self.btn_play.configure(text="\u25B6")
        if self.on_play_pause:
            self.on_play_pause(self.is_playing)

    def _repeat(self):
        """Change le mode de répétition et met en valeur le bouton si activé."""
        try:
            mode = pc.change_repeat_mode()
            mode_str = str(mode).upper()
            actif = "OFF" not in mode_str and mode_str != "NONE" and mode_str != "0"
            self.btn_repeat.configure(text_color="#1DB954" if actif else "#a0a0a0")
        except Exception as e:
            print(f"[PlayerBar] Erreur _repeat: {e}")

    def _toggle_lyrics(self):
        """Déclenche l'affichage du panneau de paroles."""
        if self.on_toggle_lyrics:
            self.on_toggle_lyrics()

    def _seek(self, value):
        """Permet à l'utilisateur de se déplacer à un moment précis dans la chanson."""
        try:
            position = int(float(value))
        except (TypeError, ValueError):
            return

        self._dernier_seek_manuel = time.time()
        pc.seek(position)
        self.lbl_temps_debut.configure(text=self._formater_temps(position))

        if self.on_seek:
            self.on_seek(value)

    def set_song(self, titre, artiste, cover_path=None):
        """Affiche les métadonnées fournies sur la barre de lecture."""
        self.lbl_titre.configure(text=titre)
        self.lbl_artiste.configure(text=artiste)
        self._set_cover(cover_path)

    def _set_cover(self, cover_path):
        """Charge et affiche l'image de la pochette si le fichier existe."""
        if cover_path and os.path.exists(cover_path):
            try:
                img = Image.open(cover_path)
                ctk_img = ctk.CTkImage(light_image=img, dark_image=img, size=(56, 56))
                if self._cover_label is None:
                    self._cover_label = ctk.CTkLabel(self.cover, text="", image=ctk_img)
                    self._cover_label.place(relx=0.5, rely=0.5, anchor="center")
                else:
                    self._cover_label.configure(image=ctk_img)
                self._cover_label.image = ctk_img
                return
            except Exception as e:
                print(f"[LireChanson] Erreur chargement pochette: {e}")

        # Réinitialisation si pas de pochette valide
        if self._cover_label is not None:
            self._cover_label.destroy()
            self._cover_label = None

    def obtenir_icone_volume(self, niveau: float) -> str:
        """Retourne l'icône Unicode correspondant au niveau sonore actuel."""
        if niveau == 0:
            return "\U0001F507" # Muet
        elif niveau < 33:
            return "\U0001F508" # Faible
        elif niveau < 66:
            return "\U0001F509" # Moyen
        else:
            return "\U0001F50A" # Fort

    def mettre_a_jour_volume(self, valeur: float):
        """Ajuste le volume sonore général et met à jour l'icône correspondante."""
        val_int = int(valeur)
        pc.change_volume(val_int)
        
        nouvelle_icone = self.obtenir_icone_volume(valeur)
        self.lbl_volume.configure(text=nouvelle_icone)

        if self.on_volume_change:
            self.on_volume_change(valeur)