"""Détection automatique du genre musical à partir du contenu audio.

Important — limite assumée de cette implémentation :
Il n'existe dans cet environnement ni jeu de données d'entraînement, ni accès
réseau vers un modèle pré-entraîné (type Hugging Face / GTZAN). Le
classifieur ci-dessous est donc un classifieur "plus proche centroïde" basé
sur des caractéristiques acoustiques (tempo, timbre, énergie...) comparées à
des profils de référence choisis à la main d'après les caractéristiques
généralement admises de chaque genre. C'est une base fonctionnelle et
totalement hors-ligne, mais **pas** un modèle de deep learning entraîné sur
des données réelles : sa précision restera modeste, en particulier sur des
morceaux ambigus ou des sous-genres.

Le classifieur est volontairement conçu comme un composant interchangeable :
``GenreClassifier.from_model_file(path)`` permet de brancher un modèle plus
robuste (par ex. un classifieur scikit-learn entraîné et sérialisé avec
joblib) sans changer le reste de l'application, dès qu'un jeu de données
d'entraînement est disponible.
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Tuple

import math

from infrastructure.ai.audio_features import extract_features, AudioFeatureExtractionError


# Échelle approximative de chaque caractéristique, utilisée pour ramener les
# distances à une échelle comparable (les unités brutes vont du ratio
# sans dimension au Hz, donc une distance euclidienne brute n'aurait aucun
# sens sans cette normalisation).
_FEATURE_SCALE: Dict[str, float] = {
    "tempo": 60.0,
    "zero_crossing_rate": 0.05,
    "rms": 0.05,
    "spectral_centroid": 1000.0,
    "spectral_bandwidth": 800.0,
    "spectral_rolloff": 1500.0,
    "spectral_contrast": 5.0,
}

# Profils de référence par genre (moyennes approximatives, établies à la main
# d'après la littérature MIR courante — PAS apprises sur un jeu de données).
_GENRE_PROFILES: Dict[str, Dict[str, float]] = {
    "Classique": {
        "tempo": 95.0, "zero_crossing_rate": 0.035, "rms": 0.04,
        "spectral_centroid": 1500.0, "spectral_bandwidth": 1500.0,
        "spectral_rolloff": 3000.0, "spectral_contrast": 22.0,
    },
    "Jazz": {
        "tempo": 118.0, "zero_crossing_rate": 0.05, "rms": 0.06,
        "spectral_centroid": 1800.0, "spectral_bandwidth": 1700.0,
        "spectral_rolloff": 3500.0, "spectral_contrast": 20.0,
    },
    "Pop": {
        "tempo": 115.0, "zero_crossing_rate": 0.06, "rms": 0.09,
        "spectral_centroid": 2200.0, "spectral_bandwidth": 1900.0,
        "spectral_rolloff": 4200.0, "spectral_contrast": 19.0,
    },
    "Rock": {
        "tempo": 128.0, "zero_crossing_rate": 0.085, "rms": 0.12,
        "spectral_centroid": 2500.0, "spectral_bandwidth": 2100.0,
        "spectral_rolloff": 4800.0, "spectral_contrast": 18.0,
    },
    "Métal": {
        "tempo": 155.0, "zero_crossing_rate": 0.13, "rms": 0.16,
        "spectral_centroid": 3400.0, "spectral_bandwidth": 2400.0,
        "spectral_rolloff": 6000.0, "spectral_contrast": 16.0,
    },
    "Électronique": {
        "tempo": 128.0, "zero_crossing_rate": 0.07, "rms": 0.13,
        "spectral_centroid": 3000.0, "spectral_bandwidth": 2200.0,
        "spectral_rolloff": 5200.0, "spectral_contrast": 21.0,
    },
    "Hip-Hop": {
        "tempo": 92.0, "zero_crossing_rate": 0.05, "rms": 0.11,
        "spectral_centroid": 1700.0, "spectral_bandwidth": 1600.0,
        "spectral_rolloff": 3200.0, "spectral_contrast": 19.0,
    },
    "Reggae": {
        "tempo": 82.0, "zero_crossing_rate": 0.045, "rms": 0.08,
        "spectral_centroid": 1700.0, "spectral_bandwidth": 1600.0,
        "spectral_rolloff": 3100.0, "spectral_contrast": 20.0,
    },
}


@dataclass
class GenrePrediction:
    genre: str
    confidence: float  # entre 0 et 1 (indicatif, pas une vraie probabilité calibrée)
    scores: Dict[str, float]  # score de proximité pour chaque genre candidat


class GenreClassifier:
    """Classifieur de genre "plus proche centroïde" sur caractéristiques
    acoustiques. Voir la docstring du module pour ses limites.
    """

    def __init__(self, profiles: Dict[str, Dict[str, float]] | None = None,
                 scale: Dict[str, float] | None = None) -> None:
        self._profiles = profiles or _GENRE_PROFILES
        self._scale = scale or _FEATURE_SCALE

    @classmethod
    def from_model_file(cls, path: Path) -> "GenreClassifier":
        """Point d'extension : charge un modèle entraîné et sérialisé
        (ex. via joblib) pour remplacer les profils heuristiques par un
        modèle réellement appris, dès qu'un jeu de données est disponible.
        """
        import joblib
        payload = joblib.load(path)
        return cls(profiles=payload["profiles"], scale=payload.get("scale"))

    def _distance(self, features: Dict[str, float], profile: Dict[str, float]) -> float:
        total = 0.0
        for key, scale in self._scale.items():
            if key not in features or key not in profile:
                continue
            diff = (features[key] - profile[key]) / scale
            total += diff * diff
        return math.sqrt(total)

    def predict_from_features(self, features: Dict[str, float]) -> GenrePrediction:
        distances = {
            genre: self._distance(features, profile)
            for genre, profile in self._profiles.items()
        }
        # Transforme les distances en scores de type "softmax" (plus la
        # distance est faible, plus le score est élevé), pour obtenir une
        # confiance indicative entre 0 et 1.
        neg_distances = {g: -d for g, d in distances.items()}
        max_val = max(neg_distances.values())
        exp_scores = {g: math.exp(v - max_val) for g, v in neg_distances.items()}
        total = sum(exp_scores.values()) or 1.0
        scores = {g: v / total for g, v in exp_scores.items()}

        best_genre = max(scores, key=lambda g: scores[g])
        return GenrePrediction(genre=best_genre, confidence=scores[best_genre], scores=scores)

    def predict(self, path: Path) -> GenrePrediction:
        features = extract_features(path)
        return self.predict_from_features(features)


genre_classifier = GenreClassifier()
