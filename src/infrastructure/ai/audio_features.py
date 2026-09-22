"""Extraction de caractéristiques audio de bas niveau, utilisées comme base
pour les fonctionnalités d'IA du lecteur (détection de genre notamment).

Toute l'analyse se fait localement avec ``librosa`` : aucun appel réseau ni
téléchargement de modèle n'est nécessaire.
"""

from pathlib import Path
from typing import Dict

import numpy as np
import librosa


# Durée (en secondes) et fréquence d'échantillonnage utilisées pour l'analyse.
# On ne charge qu'un extrait du morceau : c'est largement suffisant pour
# caractériser un genre musical et cela évite de charger un fichier long
# entièrement en mémoire.
ANALYSIS_DURATION = 60.0
ANALYSIS_SR = 22050


class AudioFeatureExtractionError(Exception):
    """Le fichier n'a pas pu être décodé/analysé pour l'extraction de caractéristiques."""


def extract_features(path: Path) -> Dict[str, float]:
    """Charge un fichier audio et calcule un petit ensemble de
    caractéristiques scalaires (tempo, timbre, énergie...) utilisées par le
    classifieur de genre.
    """
    try:
        y, sr = librosa.load(str(path), sr=ANALYSIS_SR, mono=True, duration=ANALYSIS_DURATION)
    except Exception as error:
        raise AudioFeatureExtractionError(f"Impossible d'analyser l'audio de {path} : {error}")

    if y is None or len(y) == 0:
        raise AudioFeatureExtractionError(f"Signal audio vide pour {path}")

    # Retire les silences en tête/fin pour ne pas fausser l'analyse
    y_trimmed, _ = librosa.effects.trim(y, top_db=30)
    if len(y_trimmed) > sr:  # garde une marge de sécurité si le trim est trop agressif
        y = y_trimmed

    tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
    tempo = float(np.asarray(tempo).item()) if np.ndim(tempo) else float(tempo)

    zcr = float(np.mean(librosa.feature.zero_crossing_rate(y)))
    rms = float(np.mean(librosa.feature.rms(y=y)))
    spectral_centroid = float(np.mean(librosa.feature.spectral_centroid(y=y, sr=sr)))
    spectral_bandwidth = float(np.mean(librosa.feature.spectral_bandwidth(y=y, sr=sr)))
    spectral_rolloff = float(np.mean(librosa.feature.spectral_rolloff(y=y, sr=sr)))
    spectral_contrast = float(np.mean(librosa.feature.spectral_contrast(y=y, sr=sr)))
    mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
    mfcc_means = np.mean(mfcc, axis=1)

    features = {
        "tempo": tempo,
        "zero_crossing_rate": zcr,
        "rms": rms,
        "spectral_centroid": spectral_centroid,
        "spectral_bandwidth": spectral_bandwidth,
        "spectral_rolloff": spectral_rolloff,
        "spectral_contrast": spectral_contrast,
    }
    for i, value in enumerate(mfcc_means):
        features[f"mfcc_{i}"] = float(value)

    return features
