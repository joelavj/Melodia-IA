from database.connect import connect
import mysql.connector
from models.artist_model import Artist
from models.album_model import Album
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

def find_by_name(nom:str)->Artist|None:
    cnx = connect()
    cursor = cnx.cursor()
    query = "SELECT id_artiste, nom FROM artiste WHERE nom=%s"
    cursor.execute(query, (nom,))
    artist = cursor.fetchone()
    if artist is None:
        artist = None
    else:
        artist = cast(tuple[int,str],artist)
        artist = Artist(id=artist[0],name=artist[1])
    cursor.close()
    cnx.close()
    return artist


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

def get_songs(id)->list[Song]|list:
    cnx = connect()
    cursor = cnx.cursor()
    query = "SELECT id_morceau FROM artiste_morceau WHERE id_artiste=%s"
    cursor.execute(query, (id,))
    songs = cursor.fetchall()
    if isinstance(songs, list) and len(songs) >= 1:
        songs = [Song(id=song[0]) for song in cast(list[tuple[int]], songs)]
    else:
        songs = []
    cursor.close()
    cnx.close()
    return songs

def get_albums(id)->list[Album]|list:
    cnx = connect()
    cursor = cnx.cursor()
    query = "SELECT id_album FROM artiste_album WHERE id_artiste=%s"
    cursor.execute(query, (id,))
    albums = cursor.fetchall()
    if isinstance(albums, list) and len(albums) >= 1:
        albums = [ Album(id=album[0]) for album in cast(list[tuple[int]], albums)]
    else:
        albums = []
    cursor.close()
    cnx.close()
    return albums

def find_all()->list[Artist]|list:
    cnx = connect()
    cursor = cnx.cursor()
    query = "SELECT * FROM artiste"
    cursor.execute(query)
    artists = cursor.fetchall()
    if isinstance(artists, list) and len(artists) >= 1:
        artists = [ Artist(id=artist[0],name=artist[1]) for artist in cast(list[tuple[int, str]], artists)]
    else:
        artists = []
    cursor.close()
    cnx.close()
    return artists

def find_by_id(id:int)->Artist|None:
    cnx = connect()
    cursor = cnx.cursor()
    query = "SELECT id_artiste, nom FROM artiste WHERE id_artiste=%s"
    cursor.execute(query, (id,))
    artist = cast(tuple[int, str]|None,cursor.fetchone())
    if artist is not None:
        artist = Artist(id=artist[0], name=artist[1])
    cursor.close()
    cnx.close()
    return artist
