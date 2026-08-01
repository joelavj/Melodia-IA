from database.connect import connect
import mysql.connector
from models.song_model import Song
from models.queue_model import Queue
from typing import cast

def save(song:Song)->None:
    num_ordre = get_last_num_ordre() + 1
    cnx = connect()
    cursor = cnx.cursor()
    query = "INSERT INTO playlist_morceau(id_playlist, id_morceau, num_ordre) VALUES (0, %s, %s)"
    cursor.execute(query, (song.id, num_ordre))
    cnx.commit()
    cursor.close()
    cnx.close()

def delete(song:Song)->None:
    cnx = connect()
    cursor = cnx.cursor()
    query = "DELETE FROM playlist_morceau WHERE id_playlist=0 AND id_morceau=%s"
    cursor.execute(query, (song.id,))
    cnx.commit()
    cursor.close()
    cnx.close()

def find_all()->list[Song]|list:
    cnx = connect()
    cursor = cnx.cursor()
    query = "SELECT id_morceau FROM playlist_morceau WHERE id_playlist=0 ORDER BY num_ordre ASC"
    cursor.execute(query)
    songs = cursor.fetchall()
    if songs == []:
        songs = []
    else:
        songs = [ Song(id=song[0]) for song in cast(list[tuple[int]], songs)]
    cursor.close()
    cnx.close()
    return songs

def get_last_num_ordre()->int:
    cnx = connect()
    cursor = cnx.cursor()
    query = """
        SELECT num_ordre 
        FROM playlist_morceau 
        WHERE id_playlist=0 
        ORDER BY num_ordre DESC 
        LIMIT 1
    """
    cursor.execute(query)
    last_num_ordre = cursor.fetchone()
    if last_num_ordre is None:
        last_num_ordre = 0
    else:
        last_num_ordre = cast(tuple[int], last_num_ordre)[0]
    cursor.close()
    cnx.close()
    return last_num_ordre

def clear_all()->None:
    cnx = connect()
    cursor = cnx.cursor()
    query = "DELETE FROM playlist_morceau WHERE id_playlist=0"
    cursor.execute(query)
    cnx.commit()
    cursor.close()
    cnx.close()

def find_song(song:Song)->int:
    cnx = connect()
    cursor = cnx.cursor()
    query = """
        SELECT id_morceau 
        FROM playlist_morceau 
        WHERE id_playlist=0 AND id_morceau=%s
    """
    cursor.execute(query, (song.id,))
    id_song = cursor.fetchone()
    if id_song is None:
        id_song = -1
    else:
        id_song = cast(tuple[int], id_song)[0]
    cursor.close()
    cnx.close()
    return id_song
