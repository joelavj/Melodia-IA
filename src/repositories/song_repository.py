from database.connect import connect
from pathlib import Path
from typing import cast, Literal
from models.song_model import SongSummary,Song

class SongRepository :


    def save(self, titre:str, chemin:Path, genre:str, id_repertoire:int, id_album:int, duration:int)->int | Literal[False]:
        cnx = connect()
        cursor = cnx.cursor()
        query = """
            INSERT INTO morceau(titre, chemin, genre, id_repertoire, id_album, duree) 
            VALUES (%s,%s,%s,%s,%s,%s)
        """
        cursor.execute(query, (titre, str(chemin), genre, id_repertoire, id_album, duration))
        lastrowid = cursor.lastrowid
        cnx.commit()
        cursor.close()
        cnx.close()
        return int(lastrowid) if lastrowid is not None else False


    def delete(self, id:int)->bool:
        cnx = connect()
        cursor = cnx.cursor()
        query = """
            DELETE FROM morceau 
            WHERE id_morceau=%s
        """
        cursor.execute(query, (id,))
        cnx.commit()
        result = True
        cursor.close()
        cnx.close()
        return result


    def short_find_all(self)->list:
        cnx = connect()
        cursor = cnx.cursor()
        query = """
            SELECT 
                morceau.id_morceau, morceau.titre,
                artiste.nom_scene, 
                album.titre,morceau.duree,morceau.favori
            FROM morceau
            INNER JOIN interpreter
            ON interpreter.id_morceau = morceau.id_morceau
            INNER JOIN artiste
            ON artiste.id_artiste = interpreter.id_artiste
            INNER JOIN album
            ON morceau.id_album = album.id_album;
        """
        cursor.execute(query)
        songs = cursor.fetchall()
        if songs:
            songs_tmp = []
            for song in cast(list[tuple[int,str,str,str,int,bool]],songs):
                if songs_tmp == []:
                    songs_tmp.append(SongSummary(song[0],song[1],song[2],song[3],song[4],song[5]))
                else:
                    for song_tmp in songs_tmp:
                        if song_tmp.id == song[0]:
                            song_tmp.artists += f", {song[2]}"
                            break
                    else:
                        songs_tmp.append(SongSummary(song[0],song[1],song[2],song[3],song[4],song[5]))
            songs = songs_tmp
        cursor.close()
        cnx.close()
        return songs


    def short_find_by_id(self, id:int)->SongSummary|None:
        cnx = connect()
        cursor = cnx.cursor()
        query = """
            SELECT 
                morceau.id_morceau, morceau.titre, 
                artiste.nom_scene, 
                album.titre,morceau.duree,morceau.favori
            FROM morceau
            INNER JOIN interpreter
            ON morceau.id_morceau = interpreter.id_morceau
            INNER JOIN artiste
            ON artiste.id_artiste = interpreter.id_artiste
            INNER JOIN album
            ON morceau.id_album = album.id_album
            WHERE morceau.id_morceau = %s;
        """
        cursor.execute(query, (id,))
        result = cursor.fetchall()
        song = None
        if result:
            result = cast(list[tuple[int,str,str,str,int,bool]],result)
            artists = []
            for song in result:
                artists.append(song[2])
            else:
                song = SongSummary(result[0][0],result[0][1],",".join(artists),result[0][3],result[0][4],result[0][5])
        cursor.close()
        cnx.close()
        return song


    def short_find_by_path(self, path:Path)->SongSummary|None:
        cnx = connect()
        cursor = cnx.cursor()
        query = """
            SELECT 
                morceau.id_morceau, morceau.titre, 
                artiste.nom_scene, 
                album.titre, morceau.duree,morceau.favori
            FROM morceau
            INNER JOIN interpreter
            ON morceau.id_morceau = interpreter.id_morceau
            INNER JOIN artiste
            ON artiste.id_artiste = interpreter.id_artiste
            INNER JOIN album
            ON morceau.id_album = album.id_album
            WHERE morceau.chemin = %s;
        """
        cursor.execute(query, (str(path),))
        result = cursor.fetchall()
        song = None
        if result:
            result = cast(list[tuple[int,str,str,str,int,bool]],result)
            artists = []
            for song in result:
                artists.append(song[2])
            else:
                song = SongSummary(result[0][0],result[0][1],",".join(artists),result[0][3],result[0][4],result[0][5])
        cursor.close()
        cnx.close()
        return song


    def find_by_id(self, id:int)->Song|None:
        cnx = connect()
        cursor = cnx.cursor()
        query = """
            SELECT 
                morceau.id_morceau, morceau.titre, morceau.chemin, morceau.genre, 
                artiste.nom_scene, 
                album.titre, album.pochette,morceau.duree,morceau.favori
            FROM morceau
            INNER JOIN interpreter
            ON morceau.id_morceau = interpreter.id_morceau
            INNER JOIN artiste
            ON artiste.id_artiste = interpreter.id_artiste
            INNER JOIN album
            ON morceau.id_album = album.id_album
            WHERE morceau.id_morceau = %s;
        """
        cursor.execute(query, (id,))
        result = cursor.fetchall()
        song = None
        if result:
            result = cast(list[tuple[int,str,str,str,str,str,str|None,int,int]],result)
            artists = []
            for song_tmp in result:
                if song is None:
                    song = Song(song_tmp[0],song_tmp[1],song_tmp[2],song_tmp[3],[song_tmp[4]],song_tmp[5],song_tmp[6],song_tmp[7],song_tmp[8])
                else:
                    song.artists.append(song_tmp[4])
        cursor.close()
        cnx.close()
        return song

    def update_favori(self,id_song:int,val:bool):
        cnx = connect()
        cursor = cnx.cursor()
        query = """
            UPDATE morceau
            SET favori=%s
            WHERE id_morceau=%s;
        """
        cursor.execute(query,(int(val),id_song))
        cnx.commit()
        cursor.close()
        cnx.close()

    def get_songs_favorite(self):
        cnx = connect()
        cursor = cnx.cursor()
        query = """
            SELECT id_morceau
            FROM morceau
            WHERE favori=1;
        """
        cursor.execute(query)
        result = cursor.fetchall()
        cursor.close()
        cnx.close()
        songs = []
        if result:
            for id_song in cast(list[tuple[int]],result):
                song = self.short_find_by_id(id_song[0])
                if song is not None:
                    songs.append(song)
        return songs

    def get_lyrics_path(self,id_song:int)->None|Path:
        cnx = connect()
        cursor = cnx.cursor()
        query = """
            SELECT parole
            FROM morceau
            WHERE id_morceau=%s;
        """
        cursor.execute(query,(id_song,))
        resultat = cursor.fetchone()
        cursor.close()
        cnx.close()
        lyrics = None
        if resultat is not None:
            resultat = cast(tuple,resultat)
            if resultat[0] is not None:
                lyrics = Path(cast(tuple[str],resultat)[0])        
        return lyrics

    def update_lyrics(self,id_song:int,path_lyrics:Path):
        cnx = connect()
        cursor = cnx.cursor()
        query = """
            UPDATE morceau
            SET parole=%s
            WHERE id_morceau=%s;
        """
        cursor.execute(query,(str(path_lyrics),id_song))
        cnx.commit()
        cursor.close()
        cnx.close()


song_repository = SongRepository()
