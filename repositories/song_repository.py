from database.connect import connect
from pathlib import Path

def _normalize_value(value: str, default: str = "inconnu") -> str:
    if value is None:
        value = default
    value = str(value).strip()
    return value if value else default

def find_by_path(path: Path) -> list:
    cnx = connect()
    cursor = cnx.cursor()
    query = "SELECT * FROM morceau WHERE chemin=%s"
    cursor.execute(query, (str(path),))
    resultat = cursor.fetchall()
    cursor.close()
    cnx.close()
    return resultat

def save(titre:str, chemin:Path, genre:str, id_repertoire:int, id_album:int)->int:
    titre = _normalize_value(titre)
    chemin_str = str(chemin)
    genre = _normalize_value(genre)

    cnx = connect()
    cursor = cnx.cursor()
    query = "INSERT INTO morceau(titre, chemin, genre, id_repertoire, id_album) VALUES (%s,%s,%s,%s,%s)"
    cursor.execute(query, (titre, chemin_str, genre, id_repertoire, id_album))
    lastrowid = cursor.lastrowid
    cnx.commit()
    cursor.close()
    cnx.close()
    return int(lastrowid) if lastrowid is not None else 0

def find_all()->list:
    cnx = connect()
    cursor = cnx.cursor()
    query = "SELECT * FROM morceau"
    cursor.execute(query)
    resultat = cursor.fetchall()
    cursor.close()
    cnx.close()
    return resultat

def delete(id:int)->None:
    cnx = connect()
    cursor = cnx.cursor()
    query = "DELETE FROM morceau WHERE id_morceau=%s"
    cursor.execute(query, (id,))
    cnx.commit()
    cursor.close()
    cnx.close()

def find_by_id(id:int) -> list:
    cnx = connect()
    cursor = cnx.cursor()
    query = "SELECT * FROM morceau WHERE id=%s"
    cursor.execute(query, (id,))
    resultat = cursor.fetchall()
    cursor.close()
    cnx.close()
    return resultat