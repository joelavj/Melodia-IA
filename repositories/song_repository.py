from database.connect import connect
from pathlib import Path
from typing import cast
from models.song_model import Song
from models.directory_model import Directory
from models.album_model import Album

class SongRepository :

    def _normalize_value(self, value: str, default: str = "inconnu") -> str:
        if value is None:
            value = default
        value = str(value).strip()
        return value if value else default


    def save(self, titre:str, chemin:Path, genre:str, id_repertoire:int, id_album:int)->int:
        titre = self._normalize_value(titre)
        chemin_str = str(chemin)
        genre = self._normalize_value(genre)

        cnx = connect()
        cursor = cnx.cursor()
        query = "INSERT INTO morceau(titre, chemin, genre, id_repertoire, id_album) VALUES (%s,%s,%s,%s,%s)"
        cursor.execute(query, (titre, chemin_str, genre, id_repertoire, id_album))
        lastrowid = cursor.lastrowid
        cnx.commit()
        cursor.close()
        cnx.close()
        return int(lastrowid) if lastrowid is not None else 0


    def delete(self, id:int)->None:
        cnx = connect()
        cursor = cnx.cursor()
        query = "DELETE FROM morceau WHERE id_morceau=%s"
        cursor.execute(query, (id,))
        cnx.commit()
        cursor.close()
        cnx.close()


    def find_all(self)->list:
        cnx = connect()
        cursor = cnx.cursor()
        query = """
            SELECT morceau.id_morceau, morceau.titre, morceau.chemin, morceau.genre, artiste.nom, album.id_album, album.titre, album.annee_sortie, album.pochette, repertoire.id_repertoire, repertoire.chemin 
            FROM morceau
            INNER JOIN artiste_morceau
            ON morceau.id_morceau = artiste_morceau.id_morceau
            INNER JOIN artiste
            ON artiste.id_artiste = artiste_morceau.id_artiste
            INNER JOIN album
            ON morceau.id_album = album.id_album
            INNER JOIN repertoire
            ON repertoire.id_repertoire = morceau.id_repertoire;
        """
        cursor.execute(query)
        songs = cursor.fetchall()
        if songs != []:
            songs_tmp = []
            for song in cast(list[tuple[int,str,Path,str,str,int, str,int,Path|None,int,Path,]],songs):
                if songs_tmp == []:
                    song_tmp = Song(
                        id = song[0], 
                        title = song[1], 
                        path = Path(song[2]), 
                        genre = song[3], 
                        artists = [song[4]], 
                        album = Album(
                            id=song[5],
                            name=song[6], 
                            release_year = song[7],
                            cover_path=Path(song[8]) if song[8] is not None else None
                        ), 
                        directory = Directory(
                            id=song[9], 
                            path=song[10]
                        )
                    )
                    songs_tmp.append(song_tmp)
                else:
                    for song_tmp in songs_tmp:
                        if song[0] == song_tmp.id:
                            song_tmp.artists.append(song[4])
                            break
                    else:
                        song_tmp = Song(
                            id = song[0], 
                            title = song[1], 
                            path = Path(song[2]), 
                            genre = song[3], 
                            artists = [song[4]], 
                            album = Album(
                                id=song[5],
                                name=song[6], 
                                release_year = song[7],
                                cover_path=Path(song[8]) if song[8] is not None else None
                            ), 
                            directory = Directory(
                                id=song[9], 
                                path=song[10]
                            )
                        )
                        songs_tmp.append(song_tmp)
            songs = songs_tmp
        cursor.close()
        cnx.close()
        return songs


    def find_by_id(self, id:int)->Song|None:
        cnx = connect()
        cursor = cnx.cursor()
        query = """
                SELECT morceau.id_morceau, morceau.titre, morceau.chemin, morceau.genre, artiste.nom, album.id_album, album.titre, album.annee_sortie, album.pochette, repertoire.id_repertoire, repertoire.chemin
                FROM morceau
                INNER JOIN artiste_morceau
                ON morceau.id_morceau = artiste_morceau.id_morceau
                INNER JOIN artiste
                ON artiste.id_artiste = artiste_morceau.id_artiste
                INNER JOIN album
                ON morceau.id_album = album.id_album
                INNER JOIN repertoire
                ON repertoire.id_repertoire = morceau.id_repertoire
                WHERE morceau.id_morceau = %s;
            """
        cursor.execute(query, (id,))
        resultat = cursor.fetchall()
        if resultat :
            song_tmp = None
            for song in cast(list[tuple[int,str,Path,str,str,int,str,int,Path|None,int,Path]],resultat):
                if song_tmp is None:
                    song_tmp = Song(
                        id = song[0], 
                        title = song[1], 
                        path = Path(song[2]), 
                        genre = song[3], 
                        artists = [song[4]], 
                        album = Album(
                            id=song[5],
                            name=song[6],
                            release_year=song[7],
                            cover_path=Path(song[8]) if song[8] is not None else None
                        ), 
                        directory = Directory(
                            id=song[9], 
                            path=song[10]
                        ),
                    )
                else:
                    song_tmp.artists.append(song[4])
            else:
                song = song_tmp
        else:
            song = None
        cursor.close()
        cnx.close()
        return song


    def find_by_path(self, path: Path)->Song|None:
        cnx = connect()
        cursor = cnx.cursor()
        query = """
                SELECT morceau.id_morceau, morceau.titre, morceau.chemin, morceau.genre, artiste.nom, album.id_album, album.titre, album.annee_sortie, album.pochette, repertoire.id_repertoire, repertoire.chemin
                FROM morceau
                INNER JOIN artiste_morceau
                ON morceau.id_morceau = artiste_morceau.id_morceau
                INNER JOIN artiste
                ON artiste.id_artiste = artiste_morceau.id_artiste
                INNER JOIN album
                ON morceau.id_album = album.id_album
                INNER JOIN repertoire
                ON repertoire.id_repertoire = morceau.id_repertoire
                WHERE morceau.chemin = %s;
            """
        cursor.execute(query, (str(path),))
        resultat = cursor.fetchall()
        if resultat :
            song_tmp = None
            for song in cast(list[tuple[int,str,Path,str,str,int,str,int,Path|None,int,Path]],resultat):
                if song_tmp is None:
                    song_tmp = Song(
                        id = song[0], 
                        title = song[1], 
                        path = Path(song[2]), 
                        genre = song[3], 
                        artists = [song[4]], 
                        album = Album(
                            id=song[5],
                            name=song[6],
                            release_year=song[7],
                            cover_path=Path(song[8]) if song[8] is not None else None
                        ), 
                        directory = Directory(
                            id=song[9], 
                            path=song[10]
                        ),
                    )
                else:
                    song_tmp.artists.append(song[4])
            else:
                song = song_tmp
        else:
            song = None
        cursor.close()
        cnx.close()
        return song


song_repository = SongRepository()
