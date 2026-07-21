from database.connect import connect
from pathlib import Path
from models.song_model import Song
from models.album_model import Album
from models.directory_model import Directory
from models.artist_model import Artist
from typing import cast

def _normalize_value(value: str, default: str = "inconnu") -> str:
    if value is None:
        value = default
    value = str(value).strip()
    return value if value else default

def find_by_path(path: Path)->Song|None:
    cnx = connect()
    cursor = cnx.cursor()
    query = "SELECT id_morceau, titre, chemin, genre, id_repertoire, id_album FROM morceau WHERE chemin=%s"
    cursor.execute(query, (str(path),))
    song = cursor.fetchone()
    if song is None:
        song = None
    else:
        song = cast(tuple[int,str,Path,str,int,int], song)
        song = Song(id=song[0],title=song[1],path=song[2],genre=song[3], directory=Directory(id=song[4]), album=Album(id=song[5]))
    cursor.close()
    cnx.close()
    return song

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

def find_all()->list[Song]|list:
    cnx = connect()
    cursor = cnx.cursor()
    query = "SELECT id_morceau, titre, chemin, genre, id_repertoire, id_album FROM morceau"
    cursor.execute(query)
    songs = cursor.fetchall()
    if songs == []:
        songs = []
    else:
        songs = [ Song(id=song[0],title=song[1],path=song[2],genre=song[3], directory=Directory(id=song[4]), album=Album(id=song[5])) for song in cast(list[tuple[int,str,Path,str,int,int]],songs)]
    cursor.close()
    cnx.close()
    return songs

def delete(id:int)->None:
    cnx = connect()
    cursor = cnx.cursor()
    query = "DELETE FROM morceau WHERE id_morceau=%s"
    cursor.execute(query, (id,))
    cnx.commit()
    cursor.close()
    cnx.close()

def find_by_id(id:int) -> Song|None:
    cnx = connect()
    cursor = cnx.cursor()
    query = "SELECT id_morceau, titre, chemin, genre, id_repertoire, id_album FROM morceau WHERE id=%s"
    cursor.execute(query, (id,))
    song = cursor.fetchone()
    if song is None:
        song = None
    else:
        song = cast(tuple[int,str,Path,str,int,int], song)
        song = Song(id=song[0],title=song[1],path=song[2],genre=song[3], directory=Directory(id=song[4]), album=Album(id=song[5]))
    cursor.close()
    cnx.close()
    return song

def get_artists(id:int)->list[Artist]|list:
    cnx = connect()
    cursor = cnx.cursor()
    query = "SELECT id_artist FROM artiste_morceau WHERE id_morceau=%s"
    cursor.execute(query, (id,))
    artists = cursor.fetchall()
    if artists == []:
        id_artists = []
    else:
       artists = [ Artist(id=artist[0]) for artist in cast(list[tuple[int]],artists)] 
    cursor.close()
    cnx.close()
    return artists
