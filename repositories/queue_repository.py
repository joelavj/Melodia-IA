from database.connect import connect
import mysql.connector
from models.song_model import Song
from models.queue_model import Queue
from typing import cast
from pathlib import Path


class QueueRepository : 
    def save(self, song:Song)->None:
        num_ordre = self._get_last_num_ordre() + 1
        cnx = connect()
        cursor = cnx.cursor()
        query = "INSERT INTO playlist_morceau(id_playlist, id_morceau, num_ordre) VALUES (0, %s, %s)"
        cursor.execute(query, (song.id, num_ordre))
        cnx.commit()
        cursor.close()
        cnx.close()


    def delete(self, song:Song)->None:
        cnx = connect()
        cursor = cnx.cursor()
        query = "DELETE FROM playlist_morceau WHERE id_playlist=0 AND id_morceau=%s"
        cursor.execute(query, (song.id,))
        cnx.commit()
        cursor.close()
        cnx.close()


    def find_all(self)->list[Song]|list:
        cnx = connect()
        cursor = cnx.cursor()
        query = """
            SELECT morceau.id_morceau, morceau.titre, morceau.chemin, morceau.genre 
            FROM playlist_morceau 
            INNER JOIN morceau
            ON morceau.id_morceau = playlist_morceau.id_morceau
            WHERE id_playlist=0 
            ORDER BY num_ordre ASC
        """
        cursor.execute(query)
        songs = cursor.fetchall()
        if songs != []:
            songs = [ Song(id=song[0],title=song[1],path=song[2],genre=song[3]) for song in cast(list[tuple[int,str,Path,str]], songs)]
        cursor.close()
        cnx.close()
        return songs


    def _get_last_num_ordre(self)->int:
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


    def clear_all(self)->None:
        cnx = connect()
        cursor = cnx.cursor()
        query = "DELETE FROM playlist_morceau WHERE id_playlist=0"
        cursor.execute(query)
        cnx.commit()
        cursor.close()
        cnx.close()


    def find_song(self, song:Song)->int:
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

queue_repository = QueueRepository()