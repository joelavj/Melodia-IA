import os
import mysql.connector

from utils.logger import get_logger

logger = get_logger(__name__)


def _default_config() -> dict:
    """Identifiants de connexion lus depuis l'environnement.

    En développement, ces variables peuvent être absentes (les valeurs par
    défaut ci-dessous reprennent l'ancienne configuration en dur). En
    production, définir MELODIA_DB_USER / MELODIA_DB_PASSWORD /
    MELODIA_DB_HOST / MELODIA_DB_NAME (par ex. via un fichier .env chargé
    au démarrage, non versionné) plutôt que de committer un mot de passe.
    """
    return {
        "user": os.environ.get("MELODIA_DB_USER", "root"),
        "password": os.environ.get("MELODIA_DB_PASSWORD", ""),
        "host": os.environ.get("MELODIA_DB_HOST", "127.0.0.1"),
        "database": os.environ.get("MELODIA_DB_NAME", "melodia_ia"),
    }


def connect(config=None):
    if config is None:
        config = _default_config()
    try:
        cnx = mysql.connector.connect(**config)
        # La file d'attente (playlist_repository.create_queue) suppose que
        # son id_playlist vaut littéralement 0. Sans NO_AUTO_VALUE_ON_ZERO,
        # MySQL ignore silencieusement un 0 explicite sur une colonne
        # AUTO_INCREMENT et génère un autre id, ce qui casse toute la file
        # d'attente dès l'installation. On force ce mode sur chaque connexion.
        cursor = cnx.cursor()
        cursor.execute("SET SESSION sql_mode = CONCAT(@@sql_mode, ',NO_AUTO_VALUE_ON_ZERO')")
        cursor.close()
        return cnx
    except mysql.connector.Error as error:
        logger.error("Erreur de connexion MySQL : %s", error)
        raise ConnectionError(f"Erreur de connexion MySQL : {error}") from error
