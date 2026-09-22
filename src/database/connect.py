import mysql.connector

def connect(config=None):
    if config is None:
        config = {
            "user": "root",
            "password": "",
            "host": "127.0.0.1",
            "database": "melodia_ia",
        }
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
        raise ConnectionError(f"Erreur de connexion MySQL : {error}") from error
