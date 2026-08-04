from database.connect import connect
import mysql.connector
from models.song_model import Song
from models.directory_model import Directory
from models.queue_model import Queue
from typing import cast, Optional
from pathlib import Path


class QueueRepository : 

    def __init__(self) -> None:
        cnx = connect()
        cursor = cnx.cursor()
        query = """
            INSERT INTO playlist(id_playlist,nom)  
            VALUES (0, 'queue');
        """
        try:
            cursor.execute(query)
            cnx.commit()
        except:
            pass
        cursor.close()
        cnx.close()


    def save(self, id_song:int, num_order=None)->None:
        if num_order is None:
            num_ordre = self.get_last_num_order() + 1
        cnx = connect()
        cursor = cnx.cursor()
        query = "INSERT INTO playlist_morceau(id_playlist, id_morceau, num_ordre) VALUES (0, %s, %s)"
        cursor.execute(query, (id_song, num_order))
        cnx.commit()
        cursor.close()
        cnx.close()


    def delete(self, id_song:int)->None:
        cnx = connect()
        cursor = cnx.cursor()
        query = """
            DELETE FROM playlist_morceau 
            WHERE id_playlist=0 
            AND id_morceau=%s
        """
        cursor.execute(query, (id_song,))
        cnx.commit()
        cursor.close()
        cnx.close()

    def update_order(self, begin_num_order:int, last_num_order=None, desc_order=True):
        if last_num_order is None:
            last_num_order = self.get_last_num_order()
        cnx = connect()
        cursor = cnx.cursor()
        if desc_order:
            query = """
                UPDATE playlist_morceau
                SET num_ordre = num_ordre - 1
                WHERE (num_ordre BETWEEN %s AND %s)
                AND id_playlist = 0
            """
        else:
            query = """
                UPDATE playlist_morceau
                SET num_ordre = num_ordre + 1
                WHERE (num_ordre BETWEEN %s AND %s)
                AND id_playlist = 0
            """
        cursor.execute(query,(begin_num_order,last_num_order))
        cnx.commit()
        cursor.close()
        cnx.close()


    def find_all(self)->list[Song]|list:
        cnx = connect()
        cursor = cnx.cursor()
        query = """
            SELECT morceau.id_morceau, morceau.titre, morceau.chemin, morceau.genre, repertoire.id_repertoire, repertoire.chemin
            FROM playlist_morceau 
            INNER JOIN morceau
            ON morceau.id_morceau = playlist_morceau.id_morceau
            INNER JOIN repertoire
            ON repertoire.id_repertoire = morceau.id_repertoire
            WHERE id_playlist=0 
            ORDER BY num_ordre ASC
        """
        cursor.execute(query)
        songs = cursor.fetchall()
        if songs != []:
            songs = [ Song(id=song[0],title=song[1],path=song[2],genre=song[3],directory=Directory(song[4], song[5])) for song in cast(list[tuple[int,str,Path,str,int,Path]], songs)]
        cursor.close()
        cnx.close()
        return songs




    def update_order_desc(self, id_song:int, num_ordre_initial:int, num_ordre_final:int):
        cnx = connect()
        cursor = cnx.cursor()
        query = """
            UPDATE playlist_morceau
            SET num_ordre = num_ordre - 1
            WHERE (num_ordre BETWEEN %s AND %s)
            AND id_playlist = 0

            UDPATE playlist_morceau
            SET num_ordre = %s 
            WHERE num_ordre = %s 
            AND id_morceau = %s 
            AND id_playlist = 0
        """
        cursor.execute(query, (num_ordre_initial,num_ordre_final, num_ordre_final, num_ordre_initial, id_song))
        cnx.commit()
        cursor.close()
        cnx.close()

    def update_order_asc(self, id_song:int, num_ordre_initial:int, num_ordre_final:int):
        cnx = connect()
        cursor = cnx.cursor()
        query = """
            UPDATE playlist_morceau
            SET num_ordre = num_ordre + 1
            WHERE (num_ordre BETWEEN %s AND %s)
            AND id_playlist = 0

            UDPATE playlist_morceau
            SET num_ordre = %s 
            WHERE num_ordre = %s 
            AND id_morceau = %s 
            AND id_playlist = 0
        """
        cursor.execute(query, ((num_ordre_final+1),num_ordre_initial, num_ordre_final, num_ordre_initial, id_song))
        cnx.commit()
        cursor.close()
        cnx.close()


    def find_num_ordre_song(self,id_song:int)->int:
        cnx = connect()
        cursor = cnx.cursor()
        query = """
            SELECT num_ordre 
            FROM playlist_morceau 
            WHERE id_playlist=0 AND id_morceau=%s
        """
        cursor.execute(query, (id_song,))
        num_ordre = cursor.fetchone()
        if num_ordre is None:
            num_ordre = -1
        else:
            num_ordre = cast(tuple[int], num_ordre)[0]
        cursor.close()
        cnx.close()
        return num_ordre
        

    def get_last_num_order(self)->int:
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


    def find_song(self, id_song:int)->Song|None:
        cnx = connect()
        cursor = cnx.cursor()
        query = """
            SELECT morceau.id_morceau, morceau.titre, morceau.chemin, morceau.genre, repertoire.id_repertoire, repertoire.chemin
            FROM playlist_morceau 
            INNER JOIN morceau
            ON morceau.id_morceau = playlist_morceau.id_morceau
            INNER JOIN repertoire
            ON repertoire.id_repertoire = morceau.id_repertoire
            WHERE id_playlist=0 
            AND playlist_morceau.id_morceau=%s
            ORDER BY num_ordre ASC
        """
        cursor.execute(query,(id_song,))
        song = cursor.fetchone()
        if song is not None:
            song = cast(tuple[int,str,Path,str,int,Path], song)
            song = Song(id=song[0],title=song[1],path=song[2],genre=song[3],directory=Directory(song[4], song[5]))
        cursor.close()
        cnx.close()
        return song
        

    def find_id_song(self, song:Song)->int:
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