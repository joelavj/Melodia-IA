from database.connect import connect
from models.album_model import Album
from models.artist_model import Artist

def save(titre:str, annee_sortie:str)->int:
    titre = titre.strip() if titre else ""
    if not titre:
        titre = "inconnu"

    cnx = connect()
    cursor = cnx.cursor()
    query = "INSERT INTO album(titre, annee_sortie) VALUES (%s,%s)"
    cursor.execute(query, (titre, annee_sortie))
    lastrowid = cursor.lastrowid
    cnx.commit()
    cursor.close()
    cnx.close()
    return int(lastrowid) if lastrowid is not None else 0

def link_artiste(id_artiste:int, id_album:int):
    cnx = connect()
    cursor = cnx.cursor()
    query = "INSERT INTO artiste_album(id_artiste, id_album) VALUES (%s, %s)"
    cursor.execute(query, (id_artiste, id_album))
    cnx.commit()
    cursor.close()
    cnx.close()
   
def find_by_name(titre:str)->list:
    cnx = connect()
    cursor = cnx.cursor()
    query = "SELECT * FROM album WHERE titre=%s"
    cursor.execute(query, (titre,))
    resultat = cursor.fetchall()
    cursor.close()
    cnx.close()
    return resultat

def get_songs(id:int)->list:
    cnx = connect()
    cursor = cnx.cursor()
    query = "SELECT id_morceau FROM morceau WHERE id_album=%s"
    cursor.execute(query, (id,))
    resultat = cursor.fetchall()
    cursor.close()
    cnx.close()
    return resultat

def delete(id:int)->None:
    cnx = connect()
    cursor = cnx.cursor()
    query = "DELETE FROM album WHERE id_album=%s"
    cursor.execute(query, (id,))
    cnx.commit()
    cursor.close()
    cnx.close()

def find_all()->list:
    cnx = connect()
    cursor = cnx.cursor()
    query = "SELECT * FROM album"
    cursor.execute(query)
    resultat = cursor.fetchall()
    cursor.close()
    cnx.close()
    return resultat

def get_artists(id:int)->list:
    cnx = connect()
    cursor = cnx.cursor()
    query = "SELECT id_artiste FROM artiste_album WHERE id_album=%s"
    cursor.execute(query, (id,))
    resultat = cursor.fetchall()
    cursor.close()
    cnx.close()
    return resultat

def find_by_id(id:int):
    cnx = connect()
    cursor = cnx.cursor()
    query = "SELECT * FROM album WHERE id_album=%s"
    cursor.execute(query, (id,))
    resultat = cursor.fetchone()
    cursor.close()
    cnx.close()
    return resultat
