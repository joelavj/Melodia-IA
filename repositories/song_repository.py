from database.connect import connect
from pathlib import Path
from typing import cast
from models.song_model import Song
from models.directory_model import Directory
from models.album_model import Album
from models.artist_model import Artist

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
        query = """
            INSERT INTO morceau(titre, chemin, genre, id_repertoire, id_album) 
            VALUES (%s,%s,%s,%s,%s)
        """
        cursor.execute(query, (titre, chemin_str, genre, id_repertoire, id_album))
        lastrowid = cursor.lastrowid
        cnx.commit()
        cursor.close()
        cnx.close()
        return int(lastrowid) if lastrowid is not None else 0


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
                artiste.id, artiste.nom, 
                album.id, album.titre, 
                repertoire.id_repertoire, repertoire.chemin
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
        resultat = cursor.fetchall()
        #  album.annee_sortie, repertoire.chemin
        if resultat:
            songs_tmp = []
            for song in cast(list[tuple[int,str,Path,str,int,str,int,str,int,Path]],resultat):
                if songs_tmp == []:
                    songs_tmp.append(Song(
                        id = song[0], 
                        title = song[1], 
                        path = Path(song[2]), 
                        genre = song[3], 
                        artists = [Artist(
                            id=song[4],
                            name=song[5]
                        )], 
                        album = Album(
                            id=song[6],
                            name=song[7]
                        ), 
                        directory = Directory(
                            id=song[8], 
                            path=song[9]
                        )
                    ))
                else:
                    for song_tmp in songs_tmp:
                        if song[0] == song_tmp.id:
                            song_tmp.artists.append(Artist(
                                id=song[4],
                                name=song[5]
                            ))
                            break
                    else:
                        songs_tmp.append(Song(
                            id = song[0], 
                            title = song[1], 
                            path = Path(song[2]), 
                            genre = song[3], 
                            artists = [Artist(
                                id=song[4],
                                name=song[5]
                            )], 
                            album = Album(
                                id=song[6],
                                name=song[7]
                            ), 
                            directory = Directory(
                                id=song[8], 
                                path=song[9]
                            )
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
                    artiste.id, artiste.nom, 
                    album.id_album, album.titre, 
                    repertoire.id_repertoire, repertoire.chemin
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
        song = None
        if resultat:
            for song_tmp in cast(list[tuple[int,str,Path,str,int,str,int,str,int,Path]],resultat):
                if song is None:
                    song = Song(
                        id = song_tmp[0], 
                        title = song_tmp[1], 
                        path = Path(song_tmp[2]), 
                        genre = song_tmp[3], 
                        artists = [Artist(
                            id=song_tmp[4],
                            name=song_tmp[5]
                        )], 
                        album = Album(
                            id=song_tmp[6],
                            name=song_tmp[7]
                        ), 
                        directory = Directory(
                            id=song_tmp[8], 
                            path=song_tmp[9]
                        )
                    )
                else:
                    song.artists.append(Artist(
                        id=song_tmp[4],
                        name=song_tmp[5]
                    ))
        cursor.close()
        cnx.close()
        return song

    def find_by_path(self, path:Path)->Song|None:
        cnx = connect()
        cursor = cnx.cursor()
        query = """
                SELECT 
                    morceau.id_morceau, morceau.titre, morceau.chemin, morceau.genre, 
                    artiste.id, artiste.nom, 
                    album.id_album, album.titre, 
                    repertoire.id_repertoire, repertoire.chemin
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
        cursor.execute(query, (str(path)))
        resultat = cursor.fetchall()
        song = None
        if resultat:
            for song_tmp in cast(list[tuple[int,str,Path,str,int,str,int,str,int,Path]],resultat):
                if song is None:
                    song = Song(
                        id = song_tmp[0], 
                        title = song_tmp[1], 
                        path = Path(song_tmp[2]), 
                        genre = song_tmp[3], 
                        artists = [Artist(
                            id=song_tmp[4],
                            name=song_tmp[5]
                        )], 
                        album = Album(
                            id=song_tmp[6],
                            name=song_tmp[7]
                        ), 
                        directory = Directory(
                            id=song_tmp[8], 
                            path=song_tmp[9]
                        )
                    )
                else:
                    song.artists.append(Artist(
                        id=song_tmp[4],
                        name=song_tmp[5]
                    ))
        cursor.close()
        cnx.close()
        return song


song_repository = SongRepository()
