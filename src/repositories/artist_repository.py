from database.connect import connect
from typing import cast,Literal
from models.artist_model import Artist
from models.song_model import SongSummary
from repositories.song_repository import song_repository

class ArtistRepository :

    def save(self, nom:str)->int | Literal[False]:
        cnx = connect()
        cursor = cnx.cursor()
        query = """
            INSERT INTO artiste(nom_scene) 
            VALUES (%s)
        """
        cursor.execute(query, (nom,))
        lastrowid = cursor.lastrowid
        cnx.commit()
        result = int(lastrowid) if lastrowid is not None else False
        cursor.close()
        cnx.close()
        return result


    def link_album(self, id_artiste:int, id_album:int)->bool:
        cnx = connect()
        cursor = cnx.cursor()
        query = """
            INSERT INTO produit(id_artiste, id_album) 
            VALUES (%s, %s)
        """
        cursor.execute(query, (id_artiste, id_album))
        cnx.commit()
        result = True
        cursor.close()
        cnx.close()
        return result


    def link_morceau(self, id_artiste:int, id_morceau:int)->bool:
        cnx = connect()
        cursor = cnx.cursor()
        query = """
            INSERT INTO interpreter(id_artiste, id_morceau) 
            VALUES (%s, %s);
        """
        cursor.execute(query, (id_artiste, id_morceau))
        cnx.commit()
        result = True
        cursor.close()
        cnx.close()
        return result


    def delete(self, id:int)->bool:
        cnx = connect()
        cursor = cnx.cursor()
        query = """
            DELETE FROM artiste 
            WHERE id_artiste=%s
        """
        cursor.execute(query, (id,))
        cnx.commit()
        result = True
        cursor.close()
        cnx.close()
        return result


    def find_all(self)->list:
        cnx = connect()
        cursor = cnx.cursor()
        query = """
            SELECT id_artiste, nom_scene 
            FROM artiste
        """
        cursor.execute(query)
        artists = cursor.fetchall()
        if artists:
            artists = [ Artist(id=artist[0],name=artist[1]) for artist in cast(list[tuple[int,str]],artists)]
        cursor.close()
        cnx.close()
        return artists
    

    def find_by_id(self, id:int)->Artist|None:
        cnx = connect()
        cursor = cnx.cursor()
        query = """
            SELECT id_artiste, nom_scene
            FROM artiste 
            WHERE id_artiste=%s
        """
        cursor.execute(query, (id,))
        artist = cursor.fetchone()
        if artist is not None:
            artist = cast(tuple[int, str], artist)
            artist = Artist(
                id=artist[0],
                name=artist[1]
            )
        cursor.close()
        cnx.close()
        return artist


    def find_by_name(self, name:str)->Artist|None:
        cnx = connect()
        cursor = cnx.cursor()
        query = """
            SELECT id_artiste, nom_scene 
            FROM artiste 
            WHERE nom_scene=%s
        """
        cursor.execute(query, (name,))
        artist = cursor.fetchone()
        if artist is not None:
            artist = cast(tuple[int, str], artist)
            artist = Artist(
                id=artist[0],
                name=artist[1]
            )
        cursor.close()
        cnx.close()
        return artist

    def find_songs(self,id:int)->list:
        cnx = connect()
        cursor = cnx.cursor()
        query = """
            SELECT id_morceau
            FROM interpreter
            WHERE id_artiste = %s
        """
        cursor.execute(query,(id,))
        result = cursor.fetchall()
        songs = []
        if result:
            for id_song in cast(list[tuple[int]],result):
                song = song_repository.short_find_by_id(id_song[0])
                if song is not None:
                    songs.append(song)
        cursor.close()
        cnx.close()
        return songs


artist_repository = ArtistRepository()
