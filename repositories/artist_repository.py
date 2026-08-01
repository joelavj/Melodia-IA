from database.connect import connect
import mysql.connector
from models.song_model import Song
from typing import cast

def save(nom:str)->int:
    cnx = connect()
    cursor = cnx.cursor()
    query = "INSERT INTO artiste(nom) VALUES (%s)"
    cursor.execute(query, (nom,))
    lastrowid = cursor.lastrowid
    cnx.commit()
    cursor.close()
    cnx.close()
    return int(lastrowid) if lastrowid is not None else 0

def link_album(id_artiste:int, id_album:int):
    cnx = connect()
    cursor = cnx.cursor()
    query = "INSERT IGNORE INTO artiste_album(id_artiste, id_album) VALUES (%s, %s)"
    cursor.execute(query, (id_artiste, id_album))
    cnx.commit()
    cursor.close()
    cnx.close()

def link_morceau(id_artiste:int, id_morceau:int):
    cnx = connect()
    cursor = cnx.cursor()
    query = "INSERT IGNORE INTO artiste_morceau(id_artiste, id_morceau) VALUES (%s, %s)"
    cursor.execute(query, (id_artiste, id_morceau))
    cnx.commit()
    cursor.close()
    cnx.close()

def delete(id:int)->None:
    cnx = connect()
    cursor = cnx.cursor()
    query = "DELETE FROM artiste WHERE id_artiste=%s"
    cursor.execute(query, (id,))
    cnx.commit()
    cursor.close()
    cnx.close()

def find_all()->list:
    cnx = connect()
    cursor = cnx.cursor()
    query = "SELECT id_artiste, nom FROM artiste"
    cursor.execute(query)
    artists = cursor.fetchall()
    cursor.close()
    cnx.close()
    return artists

def find_by_name(nom:str)->dict|None:
    cnx = connect()
    cursor = cnx.cursor()
    query = "SELECT id_artiste, nom FROM artiste WHERE nom=%s"
    cursor.execute(query, (nom,))
    artist = cursor.fetchone()
    if artist is not None:
        artist = cast(tuple[int,str],artist)
        artist = {
            'id': artist[0],
            'name': artist[1]
        }
    cursor.close()
    cnx.close()
    return artist

def find_by_id(id:int)->dict|None:
    cnx = connect()
    cursor = cnx.cursor()
    query = "SELECT id_artiste, nom FROM artiste WHERE id_artiste=%s"
    cursor.execute(query, (id,))
    artist = cursor.fetchone()
    if artist is not None:
        artist = cast(tuple[int, str], artist)
        artist = {
            'id': artist[0],
            'name': artist[1]
        }
    cursor.close()
    cnx.close()
    return artist
