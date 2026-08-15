from database.connect import connect
from typing import cast, Optional
from pathlib import Path
from models.song_model import Song
from models.directory_model import Directory
from models.queue_model import Queue
from models.album_model import Album
from models.artist_model import Artist


class PlaylistRepository : 

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


    def save(self, id_playlist:int, id_song:int, num_order=None)->None:
        if num_order is None:
            num_order = self.get_last_num_order(id_playlist) + 1
        cnx = connect()
        cursor = cnx.cursor()
        query = "INSERT INTO playlist_morceau(id_playlist, id_morceau, num_ordre) VALUES (%s, %s, %s)"
        cursor.execute(query, (id_playlist,id_song, num_order))
        cnx.commit()
        cursor.close()
        cnx.close()


    def delete_song(self, id_playlist:int, id_song:int)->None:
        cnx = connect()
        cursor = cnx.cursor()
        query = """
            DELETE FROM playlist_morceau 
            WHERE id_playlist=%s
            AND id_morceau=%s
        """
        cursor.execute(query, (id_playlist, id_song,))
        cnx.commit()
        cursor.close()
        cnx.close()

    def update_order(self, id_playlist:int, begin_num_order:int, last_num_order=None, desc_order=True):
        if last_num_order is None:
            last_num_order = self.get_last_num_order(id_playlist)
        cnx = connect()
        cursor = cnx.cursor()
        if desc_order:
            query = """
                UPDATE playlist_morceau
                SET num_ordre = num_ordre - 1
                WHERE (num_ordre BETWEEN %s AND %s)
                AND id_playlist = %s
            """
        else:
            query = """
                UPDATE playlist_morceau
                SET num_ordre = num_ordre + 1
                WHERE (num_ordre BETWEEN %s AND %s)
                AND id_playlist = %s
            """
        cursor.execute(query,(begin_num_order,last_num_order), id_playlist)
        cnx.commit()
        cursor.close()
        cnx.close()


    def get_songs(self,id_playlist:int)->list:
        cnx = connect()
        cursor = cnx.cursor()
        query = """
            SELECT 
                morceau.id_morceau, morceau.titre, morceau.chemin, morceau.genre, 
                artiste.nom,
                album.titre, album.pochette,
            FROM playlist_morceau 
            INNER JOIN morceau
            ON morceau.id_morceau = playlist_morceau.id_morceau
            INNER JOIN album 
            ON album.id_album = morceau.id_album
            INNER JOIN artiste_morceau
            ON artiste_morceau.id_morceau = morceau.id_morceau
            INNER JOIN artiste
            ON artiste.id_artiste = artiste_morceau.id_artiste
            WHERE id_playlist=%s
            ORDER BY num_ordre ASC
        """
        cursor.execute(query,id_playlist)
        resultat = cursor.fetchall()
        #  album.annee_sortie, repertoire.chemin
        if resultat:
            songs_tmp = []
            for song in cast(list[tuple[int,str,Path,str,str,str,Path|None]],resultat):
                    if songs_tmp == []:
                        songs_tmp.append(Song(
                            id = song[0], 
                            title = song[1], 
                            path = Path(song[2]), 
                            genre = song[3], 
                            artists = song[4],
                            album = song[5],
                            cover_path=Path(song[6]) if song[6] is not None else None
                        ))
                    else:
                        for song_tmp in songs_tmp:
                            if song[0] == song_tmp.id:
                                song_tmp.artists += " , " + song[4]
                                break
                        else:
                            songs_tmp.append(Song(
                                id = song[0], 
                                title = song[1], 
                                path = Path(song[2]), 
                                genre = song[3], 
                                artists = song[4],
                                album = song[5],
                                cover_path=Path(song[6]) if song[6] is not None else None
                            ))
            songs = songs_tmp
        else:
            songs = []
        cursor.close()
        cnx.close()
        return songs
    

    def update_order_desc(self, id_playlist:int, id_song:int, num_ordre_initial:int, num_ordre_final:int):
        cnx = connect()
        cursor = cnx.cursor()
        query = """
            UPDATE playlist_morceau
            SET num_ordre = num_ordre - 1
            WHERE (num_ordre BETWEEN %s AND %s)
            AND id_playlist = %s

            UDPATE playlist_morceau
            SET num_ordre = %s 
            WHERE num_ordre = %s 
            AND id_morceau = %s 
            AND id_playlist = %s
        """
        cursor.execute(query, (num_ordre_initial,num_ordre_final, id_playlist, num_ordre_final, num_ordre_initial, id_song), id_playlist)
        cnx.commit()
        cursor.close()
        cnx.close()

    def update_order_asc(self, id_playlist:int, id_song:int, num_ordre_initial:int, num_ordre_final:int):
        cnx = connect()
        cursor = cnx.cursor()
        query = """
            UPDATE playlist_morceau
            SET num_ordre = num_ordre + 1
            WHERE (num_ordre BETWEEN %s AND %s)
            AND id_playlist = %s

            UDPATE playlist_morceau
            SET num_ordre = %s 
            WHERE num_ordre = %s 
            AND id_morceau = %s 
            AND id_playlist = %s
        """
        cursor.execute(query, ((num_ordre_final+1),num_ordre_initial, id_playlist, num_ordre_final, num_ordre_initial, id_song), id_playlist)
        cnx.commit()
        cursor.close()
        cnx.close()


    def find_num_ordre_song(self,id_playlist:int, id_song:int)->int:
        cnx = connect()
        cursor = cnx.cursor()
        query = """
            SELECT num_ordre 
            FROM playlist_morceau 
            WHERE id_playlist=%s AND id_morceau=%s
        """
        cursor.execute(query, (id_playlist, id_song))
        num_ordre = cursor.fetchone()
        if num_ordre is None:
            num_ordre = -1
        else:
            num_ordre = cast(tuple[int], num_ordre)[0]
        cursor.close()
        cnx.close()
        return num_ordre
        

    def get_last_num_order(self,id_playlist:int)->int:
        cnx = connect()
        cursor = cnx.cursor()
        query = """
            SELECT num_ordre 
            FROM playlist_morceau 
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


    def clear_playlist(self,id_playlist:int)->None:
        cnx = connect()
        cursor = cnx.cursor()
        query = "DELETE FROM playlist_morceau WHERE id_playlist=%s"
        cursor.execute(query,(id_playlist,))
        cnx.commit()
        cursor.close()
        cnx.close()


    def find_song(self, id_playlist:int, id_song:int)->Song|None:
        cnx = connect()
        cursor = cnx.cursor()
        query = """
            SELECT 
                morceau.id_morceau, morceau.titre, morceau.chemin, morceau.genre, 
                artiste.nom
                album.titre, album.pochette,
            FROM playlist_morceau 
            INNER JOIN morceau
            ON morceau.id_morceau = playlist_morceau.id_morceau
            INNER JOIN artiste_morceau
            ON artiste_morceau.id_morceau = morceau.id_morceau
            INNER JOIN artiste
            ON artiste.id_artiste = artiste_morceau.id_artiste
            INNER JOIN album
            ON album.id_album = morceau.id_album
            WHERE id_playlist=0 
            AND playlist_morceau.id_morceau=%s
        """
        cursor.execute(query, (id,))
        resultat = cursor.fetchall()
        song = None
        if resultat:
            for song_tmp in cast(list[tuple[int,str,Path,str,str,str,Path|None]],resultat):
                if song is None:
                    song = Song(
                        id = song_tmp[0], 
                        title = song_tmp[1], 
                        path = Path(song_tmp[2]), 
                        genre = song_tmp[3], 
                        artists = song_tmp[4],
                        album = song_tmp[5],
                        cover_path=Path(song_tmp[6]) if song_tmp[6] is not None else None                                
                    )
                else:
                    song.artists += " , " + song_tmp[4]
        cursor.close()
        cnx.close()
        return song
                


playlist_repository = PlaylistRepository()