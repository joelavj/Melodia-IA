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
        return mysql.connector.connect(**config)
    except mysql.connector.Error as error:
        raise ConnectionError(f"Erreur de connexion MySQL : {error}") from error
