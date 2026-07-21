from database.connect import connect
from models.album_model import Album
from models.artist_model import Artist
from models.song_model import Song
from typing import cast
import repositories.artist_repository as artist_repository

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
   
def find_by_name(titre:str)->Album|None:
    cnx = connect()
    cursor = cnx.cursor()
    query = "SELECT id_album, titre, annee_sortie FROM album WHERE titre=%s"
    cursor.execute(query, (titre,))
    album = cursor.fetchone()
    if album is None:
        album = None
    else:
        album =  cast(tuple[int,str,int], album)
        album = Album(id=album[0],title=album[1],release_year=album[2])
    cursor.close()
    cnx.close()
    return album

def get_songs(id:int)->list[Song]|list:
    cnx = connect()
    cursor = cnx.cursor()
    query = "SELECT id_morceau FROM morceau WHERE id_album=%s"
    cursor.execute(query, (id,))
    songs = cursor.fetchall()
    if songs == []:
        songs = []
    else:
        songs = [ Song(id=song[0]) for song in cast(list[tuple[int]], songs)]
    cursor.close()
    cnx.close()
    return songs

def delete(id:int)->None:
    cnx = connect()
    cursor = cnx.cursor()
    query = "DELETE FROM album WHERE id_album=%s"
    cursor.execute(query, (id,))
    cnx.commit()
    cursor.close()
    cnx.close()

def find_all()->list[Album]|list:
    cnx = connect()
    cursor = cnx.cursor()
    query = "SELECT id_album, titre, annee_sortie FROM album"
    cursor.execute(query)
    albums = cursor.fetchall()
    if albums == []:
        albums = []
    else:
        albums = [ Album(id=album[0], title=album[1], release_year=album[2]) for album in cast(list[tuple[int, str, int]], albums)]
    cursor.close()
    cnx.close()
    return albums

def get_artists(id:int)->list[Artist]|list:
    cnx = connect()
    cursor = cnx.cursor()
    query = "SELECT id_artiste FROM artiste_album WHERE id_album=%s"
    cursor.execute(query, (id,))
    artists = cursor.fetchall()
    if artists == []:
        artists = []
    else:
        artists = [ Artist(id=artist[0]) for artist in cast(list[tuple[int]], artists) ]
    cursor.close()
    cnx.close()
    return artists

def find_by_id(id:int)->Album|None:
    cnx = connect()
    cursor = cnx.cursor()
    query = "SELECT id_album, titre, annee_sortie FROM album WHERE id_album=%s"
    cursor.execute(query, (id,))
    album = cast(tuple[int,str,int]|None,cursor.fetchone())
    if album is not None:
        album = Album(id=album[0], title=album[1], release_year=album[2])
    cursor.close()
    cnx.close()
    return album

