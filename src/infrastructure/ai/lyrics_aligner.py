"""Estimation automatique des instants (timestamps) de chaque ligne de
paroles à partir du contenu audio, pour générer un fichier LRC synchronisé
sans intervention manuelle.

Limite assumée : il ne s'agit pas d'un alignement parole-texte par
reconnaissance vocale (ASR + forced alignment), qui nécessiterait un modèle
de transcription non disponible hors-ligne dans cet environnement. On
combine à la place :

1. Une répartition proportionnelle à la longueur de chaque ligne sur la
   portion "active" du morceau (silences de début/fin exclus) ;
2. Un calage de chaque estimation sur l'onset (attaque sonore) détecté le
   plus proche, pour coller aux véritables évènements audio plutôt qu'à une
   simple interpolation linéaire aveugle.

Le résultat est une estimation raisonnable, à affiner si besoin avec les
outils de synchronisation manuelle déjà existants (``generate_manual_sync``).
"""

from pathlib import Path
from typing import List, Sequence

import numpy as np
import librosa


# Garde-fou mémoire : au-delà, on tronque l'analyse (une chanson dépasse
# rarement 10 minutes).
MAX_ANALYSIS_DURATION = 600.0
ANALYSIS_SR = 22050
# Écart minimal imposé entre deux lignes consécutives affichées.
MIN_GAP_SECONDS = 0.6


class LyricsAlignmentError(Exception):
    """L'audio n'a pas pu être chargé/analysé pour la synchronisation automatique."""


def estimate_line_timestamps(lines: Sequence[str], audio_path: Path) -> List[float]:
    """Retourne une estimation du timestamp (en secondes) de chaque ligne de
    ``lines`` (déjà nettoyée : pas de ligne vide), dans l'ordre.
    """
    if not lines:
        return []

    try:
        y, sr = librosa.load(str(audio_path), sr=ANALYSIS_SR, mono=True, duration=MAX_ANALYSIS_DURATION)
    except Exception as error:
        raise LyricsAlignmentError(
            f"Impossible de charger l'audio pour la synchronisation automatique : {error}"
        )

    if y is None or len(y) == 0:
        raise LyricsAlignmentError("Signal audio vide, synchronisation automatique impossible.")

    _, active_interval = librosa.effects.trim(y, top_db=30)
    start_offset = float(active_interval[0]) / sr
    end_offset = float(active_interval[1]) / sr
    active_duration = max(end_offset - start_offset, 1.0)

    onset_times = librosa.onset.onset_detect(y=y, sr=sr, units='time', backtrack=True)

    # Répartition proportionnelle à la longueur (en caractères) de chaque
    # ligne : une ligne plus longue occupe en général plus de temps qu'une
    # ligne courte.
    lengths = [max(len(line), 1) for line in lines]
    total_len = sum(lengths)
    cumulative = 0
    target_times = []
    for length in lengths:
        proportion = cumulative / total_len
        target_times.append(start_offset + proportion * active_duration)
        cumulative += length

    # Calage sur l'onset détecté le plus proche, dans une fenêtre de
    # tolérance proportionnelle à l'espacement moyen attendu entre lignes.
    tolerance = max((active_duration / max(len(lines), 1)) * 0.5, 1.0)
    snapped_times: List[float] = []
    for target in target_times:
        snapped = target
        if len(onset_times) > 0:
            idx = int(np.argmin(np.abs(onset_times - target)))
            candidate = float(onset_times[idx])
            if abs(candidate - target) <= tolerance:
                snapped = candidate
        snapped_times.append(snapped)

    # Garantit une progression strictement croissante avec un écart minimal,
    # pour ne jamais afficher deux lignes au même instant (ou dans le
    # désordre) après le calage sur les onsets.
    for i in range(1, len(snapped_times)):
        if snapped_times[i] <= snapped_times[i - 1] + MIN_GAP_SECONDS:
            snapped_times[i] = snapped_times[i - 1] + MIN_GAP_SECONDS

    return snapped_times
