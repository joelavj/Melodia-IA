"""Configuration centralisée du logging de l'application.

Remplace les appels ``print()`` disséminés dans le code par un logger
standard : sortie console + fichier journalisé (rotatif), niveau
configurable via la variable d'environnement ``MELODIA_LOG_LEVEL``
(DEBUG/INFO/WARNING/ERROR, défaut INFO).

Utilisation dans un module :

    from utils.logger import get_logger
    logger = get_logger(__name__)

    logger.info("Ajout avec succès du répertoire: %s", path)
    logger.warning("Erreur de suppression du répertoire")
    logger.error("Erreur pendant le scan : %s", error, exc_info=True)
"""

import logging
import os
from logging.handlers import RotatingFileHandler
from pathlib import Path

# racine du projet (.. /.. depuis src/utils/logger.py) -> <projet>/logs/
_LOG_DIR = Path(__file__).resolve().parents[2] / "logs"
_LOG_FILE = _LOG_DIR / "melodia_ia.log"

_configured = False


def _configure_root_logger() -> None:
    global _configured
    if _configured:
        return

    _LOG_DIR.mkdir(parents=True, exist_ok=True)

    level_name = os.environ.get("MELODIA_LOG_LEVEL", "INFO").upper()
    level = getattr(logging, level_name, logging.INFO)

    formatter = logging.Formatter(
        "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    file_handler = RotatingFileHandler(
        _LOG_FILE, maxBytes=2_000_000, backupCount=3, encoding="utf-8"
    )
    file_handler.setFormatter(formatter)

    root = logging.getLogger("melodia_ia")
    root.setLevel(level)
    root.addHandler(console_handler)
    root.addHandler(file_handler)
    # Évite la double propagation vers le root logger par défaut de Python.
    root.propagate = False

    _configured = True


def get_logger(name: str) -> logging.Logger:
    """Retourne un logger enfant du logger racine ``melodia_ia``.

    Appeler avec ``__name__`` depuis chaque module pour avoir des logs
    correctement attribués (ex: ``melodia_ia.services.scanner_service``).
    """
    _configure_root_logger()
    return logging.getLogger(f"melodia_ia.{name}")
