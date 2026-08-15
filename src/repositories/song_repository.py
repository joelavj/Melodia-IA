from database.connect import connect
from pathlib import Path
from typing import cast
from models.song_model import Song

class SongRepository :

    def save(self, titre:str, chemin:Path, genre:str, id_repertoire:int, id_album:int)->int:
        cnx = connect()
        cursor = cnx.cursor()
        query = """
            INSERT INTO morceau(titre, chemin, genre, id_repertoire, id_album) 
            VALUES (%s,%s,%s,%s,%s)
        """
        cursor.execute(query, (titre, str(chemin), genre, id_repertoire, id_album))
        lastrowid = cursor.lastrowid
        cnx.commit()
        cursor.close()
        cnx.close()
        return int(lastrowid) if lastrowid is not None else -1


    def delete(self, id:int)->None:
        cnx = connect()
        cursor = cnx.cursor()
        query = """
            DELETE FROM morceau 
            WHERE id_morceau=%s
        """
        cursor.execute(query, (id,))
        cnx.commit()
        cursor.close()
        cnx.close()


    def find_all(self)->list:
        cnx = connect()
        cursor = cnx.cursor()
        query = """
            SELECT 
                morceau.id_morceau, morceau.titre, morceau.chemin, morceau.genre, 
                artiste.nom, 
                album.titre, album.pochette,
            FROM morceau
            INNER JOIN artiste_morceau
            ON morceau.id_morceau = artiste_morceau.id_morceau
            INNER JOIN artiste
            ON artiste.id_artiste = artiste_morceau.id_artiste
            INNER JOIN album
            ON morceau.id_album = album.id_album
        """
        cursor.execute(query)
        resultat = cursor.fetchall()
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


    def find_by_id(self, id:int)->Song|None:
        cnx = connect()
        cursor = cnx.cursor()
        query = """
                SELECT 
                    morceau.id_morceau, morceau.titre, morceau.chemin, morceau.genre, 
                    artiste.nom, 
                    album.titre, album.pochette,
                FROM morceau
                INNER JOIN artiste_morceau
                ON morceau.id_morceau = artiste_morceau.id_morceau
                INNER JOIN artiste
                ON artiste.id_artiste = artiste_morceau.id_artiste
                INNER JOIN album
                ON morceau.id_album = album.id_album
                WHERE morceau.id_morceau = %s;
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


    def find_by_path(self, path:Path)->Song|None:
        cnx = connect()
        cursor = cnx.cursor()
        query = """
                SELECT 
                    morceau.id_morceau, morceau.titre, morceau.chemin, morceau.genre, 
                    artiste.nom, 
                    album.titre, album.pochette,
                FROM morceau
                INNER JOIN artiste_morceau
                ON morceau.id_morceau = artiste_morceau.id_morceau
                INNER JOIN artiste
                ON artiste.id_artiste = artiste_morceau.id_artiste
                INNER JOIN album
                ON morceau.id_album = album.id_album
                WHERE morceau.chemin = %s;
            """
        cursor.execute(query, (str(path)))
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


song_repository = SongRepository()
