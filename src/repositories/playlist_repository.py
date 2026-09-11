from database.connect import connect
from typing import cast
from repositories.song_repository import song_repository
from models.playlist_model import Playlist

class PlaylistRepository : 

    
    def create_queue(self):
        cnx = connect()
        cursor = cnx.cursor()
        query = """
            INSERT INTO playlist(id_playlist,nom)  
            VALUES (0,"queue");
        """
        cursor.execute(query)
        cnx.commit()
        cursor.close()
        cnx.close()

    def create_playlist(self, name:str)->int:
        cnx = connect()
        cursor = cnx.cursor()
        query = """
            INSERT INTO playlist(nom)  
            VALUES (%s);
        """
        cursor.execute(query,(name,))
        cnx.commit()
        lastrowid = cursor.lastrowid

        cursor.close()
        cnx.close()
        return int(lastrowid) if lastrowid is not None else 0

    def rename_playlist(self, id_playlist:int, name:str):
        cnx = connect()
        cursor = cnx.cursor()
        query = """
            UPDATE playlist
            SET nom = %s
            WHERE id_playlist = %s;
        """
        cursor.execute(query,(name,id_playlist))
        cnx.commit()
        cursor.close()
        cnx.close()

    def save(self, id_playlist:int, id_song:int)->bool:
        num_order = self.get_last_num_order(id_playlist) + 1
        cnx = connect()
        cursor = cnx.cursor()
        query = """
            INSERT INTO contenir(id_playlist, id_morceau, num_ordre) 
            VALUES (%s, %s, %s)
        """
        cursor.execute(query, (id_playlist, id_song, num_order))
        cnx.commit()
        cursor.close()
        cnx.close()
        return True


    def delete_song(self, id_playlist:int, id_song:int)->bool:
        cnx = connect()
        cursor = cnx.cursor()
        query = """
            DELETE FROM contenir 
            WHERE id_playlist=%s
            AND id_morceau=%s
        """
        cursor.execute(query, (id_playlist,id_song))
        cnx.commit()
        cursor.close()
        cnx.close()
        return True

    def get_songs(self,id_playlist:int)->list:
        cnx = connect()
        cursor = cnx.cursor()
        query = """
            SELECT id_morceau
            FROM contenir
            WHERE id_playlist=%s
            ORDER BY num_ordre ASC
        """
        cursor.execute(query,(id_playlist,))
        result = cursor.fetchall()
        songs = []
        if result:
            id_songs = [id_song[0] for id_song in cast(list[tuple[int]],result)]
            for id_song in id_songs:
                song = song_repository.short_find_by_id(id_song)
                if song is not None:
                    songs.append(song)
        cursor.close()
        cnx.close()
        return songs
        
            

    def get_last_num_order(self,id_playlist)->int:
        cnx = connect()
        cursor = cnx.cursor()
        query = """
            SELECT num_ordre 
            FROM contenir 
            WHERE id_playlist=%s
            ORDER BY num_ordre DESC 
            LIMIT 1
        """
        cursor.execute(query,(id_playlist,))
        last_num_ordre = cursor.fetchone()
        if last_num_ordre is None:
            last_num_ordre = 0
        else:
            last_num_ordre = cast(tuple[int], last_num_ordre)[0]
        cursor.close()
        cnx.close()
        return last_num_ordre


    def clear_playlist(self,id_playlist:int)->bool:
        cnx = connect()
        cursor = cnx.cursor()
        query = """
            DELETE FROM contenir 
            WHERE id_playlist=%s
        """
        cursor.execute(query,(id_playlist,))
        cnx.commit()
        result = True
        cursor.close()
        cnx.close()
        return result

    def song_is_here(self,id_playlist:int, id_song:int)->bool:
        cnx = connect()
        cursor = cnx.cursor()
        query = """
            SELECT id_morceau
            FROM contenir
            WHERE id_playlist=%s and id_morceau=%s;
        """    
        cursor.execute(query,(id_playlist,id_song))
        result = False
        if cursor.fetchone() is not None:
            result = True
        cursor.close()
        cnx.close()
        return result

    def playlist_is_here(self,name:str)->bool:
        cnx = connect()
        cursor = cnx.cursor()
        query = """
            SELECT id_playlist
            FROM playlist
            WHERE nom=%s;
        """    
        cursor.execute(query,(name,))
        result = False
        if cursor.fetchone() is not None:
            result = True
        cursor.close()
        cnx.close()
        return result
        
    def delete_playlist(self, id_playlist):
        cnx = connect()
        cursor = cnx.cursor()
        query = """
            DELETE FROM playlist
            WHERE id_playlist=%s;
        """
        cursor.execute(query,(id_playlist,))
        cnx.commit()
        cursor.close()
        cnx.close()

    def find_all(self)->list:
        cnx = connect()
        cursor = cnx.cursor()
        query = """
            SELECT id_playlist, nom
            FROM playlist
            WHERE id_playlist != 0;
        """
        cursor.execute(query)
        result = cursor.fetchall()
        playlists = []
        if result:
            playlists = list(map(lambda playlist:Playlist(id=playlist[0],name=playlist[1]),cast(list[tuple[int,str]],result)))
        cursor.close()
        cnx.close()
        return playlists

playlist_repository = PlaylistRepository()