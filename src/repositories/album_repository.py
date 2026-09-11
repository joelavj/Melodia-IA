from database.connect import connect
from typing import cast, Literal
from pathlib import Path
from typing import Optional
from models.album_model import Album
from models.song_model import SongSummary
from repositories.song_repository import song_repository

class AlbumRepository :

    def save(self, titre:str, annee_sortie:str, cover_path:Optional[Path]=None)->int | Literal[False]:
        cnx = connect()
        cursor = cnx.cursor()
        query = """
            INSERT INTO album(titre, annee_sortie, pochette) 
            VALUES (%s,%s,%s)
        """

        cursor.execute(query, (titre, annee_sortie,str(cover_path)))
        lastrowid = cursor.lastrowid
        cnx.commit()
        cursor.close()
        cnx.close()
        return int(lastrowid) if lastrowid is not None else False
    

    def delete(self, id:int)->bool:
        cnx = connect()
        cursor = cnx.cursor()
        query = """
            DELETE FROM album 
            WHERE id_album=%s
        """
        cursor.execute(query, (id,))
        cnx.commit()
        cursor.close()
        cnx.close()
        return True


    def find_all(self)->list:
        cnx = connect()
        cursor = cnx.cursor()
        query = """
            SELECT 
                album.id_album, album.titre, artiste.nom_scene, album.annee_sortie, album.pochette
            FROM album
            INNER JOIN produit
            ON produit.id_album = album.id_album
            INNER JOIN artiste
            ON artiste.id_artiste = produit.id_artiste
        """
        cursor.execute(query)
        result = cursor.fetchall()
        albums = []
        if result:
            albums_tmp = []
            for album in cast(list[tuple[int,str,str,int,str|None]],result):
                if albums_tmp == []:
                    albums_tmp.append(Album(*album))
                else:
                    for album_tmp in albums_tmp:
                        if album_tmp.id == album[0]:
                            album_tmp.artists += " , " + album[2]
                            break
                    else:
                        albums_tmp.append(Album(*album))
            else:
                albums = albums_tmp
        cursor.close()
        cnx.close()
        return albums
    
    
    
    def find_by_id(self, id:int)->Album|None:
        cnx = connect()
        cursor = cnx.cursor()
        query = """
            SELECT 
                album.id_album, album.titre, artiste.nom_scene, album.annee_sortie, album.pochette
            FROM album
            INNER JOIN produit
            ON produit.id_album = album.id_album
            INNER JOIN artiste
            ON artiste.id_artiste = produit.id_artiste
            WHERE album.id_album=%s;
        """
        cursor.execute(query, (id,))
        result = cursor.fetchall()
        album = None
        if result:
            result = cast(list[tuple[int,str,str,int,str|None]],result)
            artists = []
            for album_tmp in result:
                artists.append(album_tmp[2])
            else:
                album = Album(*result[0])
                album.artists = ", ".join(artists)
        cursor.close()
        cnx.close()
        return album

    def find_by_name(self, name:str)->Album|None:
        cnx = connect()
        cursor = cnx.cursor()
        query = """
            SELECT 
                album.id_album, album.titre, artiste.nom_scene, album.annee_sortie, album.pochette
            FROM album
            INNER JOIN produit
            ON produit.id_album = album.id_album
            INNER JOIN artiste
            ON artiste.id_artiste = produit.id_artiste
            WHERE album.titre=%s;
        """
        cursor.execute(query, (name,))
        result = cursor.fetchall()
        album = None
        if result:
            result = cast(list[tuple[int,str,str,int,str|None]],result)
            artists = []
            for album_tmp in result:
                artists.append(album_tmp[2])
            else:
                album = Album(*result[0])
                album.artists = ", ".join(artists)
        cursor.close()
        cnx.close()
        return album

    def find_songs(self,id:int)->list:
        cnx = connect()
        cursor = cnx.cursor()
        query = """
            SELECT 
                id_morceau
            FROM morceau
            WHERE id_album=%s;
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


album_repository = AlbumRepository()