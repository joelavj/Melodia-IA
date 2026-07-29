from database.connect import connect
from typing import cast

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

def find_all()->list:
    cnx = connect()
    cursor = cnx.cursor()
    query = "SELECT id_album, titre, annee_sortie FROM album"
    cursor.execute(query)
    albums = cursor.fetchall()
    cursor.close()
    cnx.close()
    return albums
   
def find_by_name(titre:str)->dict|None:
    cnx = connect()
    cursor = cnx.cursor()
    query = "SELECT id_album, titre, annee_sortie FROM album WHERE titre=%s"
    cursor.execute(query, (titre,))
    album = cursor.fetchone()
    if album is None:
        album = None
    else:
        album =  cast(tuple[int,str,int],album)
        album = {
            'id': album[0],
            'title': album[1],
            'release_year': album[2]
        }
    cursor.close()
    cnx.close()
    return album

def find_by_id(id:int)->dict|None:
    cnx = connect()
    cursor = cnx.cursor()
    query = "SELECT id_album, titre, annee_sortie FROM album WHERE id_album=%s"
    cursor.execute(query, (id,))
    album =cursor.fetchone()
    if album is not None:
        album = cast(tuple[int, str, int], album)
        album = {
            'id': album[0],
            'title': album[1],
            'release_year': album[2]
        }
    cursor.close()
    cnx.close()
    return album
