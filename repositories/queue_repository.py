from database.connect import connect
import mysql.connector
from models.song_model import Song
from models.queue_model import Queue
from typing import cast

def create(queue:Queue)->Queue:
    cnx = connect()
    cursor = cnx.cursor()
    query = "INSERT INTO queue (nom) VALUES (%s)"
    cursor.execute(query, (queue.name,))
    queue.id = cast(int, cursor.lastrowid)
    cnx.commit()
    cursor.close()
    cnx.close()
    return queue

def save(queue:Queue, song:Song):
    if not isinstance(song.id, int):
        return
    cnx = connect()
    cursor = cnx.cursor()
    query = "INSERT INTO queue_morceau (id_morceau, id_queue) VALUES (%s, %s)"
    cursor.execute(query, (song.id, queue.id))
    cnx.commit()
    cursor.close()
    cnx.close()

def delete(queue:Queue, song:Song):
    cnx = connect()
    cursor = cnx.cursor()
    query = "DELETE FROM queue_morceau WHERE id_morceau=%s and id_queue=%s"
    cursor.execute(query, (song.id,queue.id))
    cnx.commit()
    cursor.close()
    cnx.close()

def destroy(queue:Queue):
    cnx = connect()
    cursor = cnx.cursor()
    query = "DELETE FROM queue WHERE id_queue=%s"
    cursor.execute(query, (queue.id,))
    cnx.commit()
    cursor.close()
    cnx.close()


def clear(queue:Queue):
    cnx = connect()
    cursor = cnx.cursor()
    query = "DELETE FROM queue_morceau WHERE id_queue=%s"
    cursor.execute(query, (queue.id,))
    cnx.commit()
    cursor.close()
    cnx.close()

def find_all(queue:Queue)->list[Song]|list:
    cnx = connect()
    cursor = cnx.cursor()
    query = "SELECT id_morceau FROM queue_morceau WHERE id_queue=%s"
    cursor.execute(query, (queue.id,))
    songs = cursor.fetchall()
    if songs is None:
        songs = []
    else:
        songs = [ Song(id=song[0]) for song in cast(list[tuple[int]], songs)]
    cursor.close()
    cnx.close()
    return songs