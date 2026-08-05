from database.connect import connect
from typing import cast, Optional
from pathlib import Path
from models.album_model import Album

class AlbumRepository :

    def save(self, titre:str, annee_sortie:str, cover_path=None)->int:
        titre = titre.strip() if titre else ""
        if not titre:
            titre = "inconnu"
        cnx = connect()
        cursor = cnx.cursor()
        query = "INSERT INTO album(titre, annee_sortie, pochette) VALUES (%s,%s,%s)"
        cursor.execute(query, (titre, annee_sortie, str(cover_path)))
        lastrowid = cursor.lastrowid
        cnx.commit()
        cursor.close()
        cnx.close()
        return int(lastrowid) if lastrowid is not None else 0


    def link_artiste(self, id_artiste:int, id_album:int):
        cnx = connect()
        cursor = cnx.cursor()
        query = "INSERT INTO artiste_album(id_artiste, id_album) VALUES (%s, %s)"
        cursor.execute(query, (id_artiste, id_album))
        cnx.commit()
        cursor.close()
        cnx.close()

    def find_all(self)->list:
        cnx = connect()
        cursor = cnx.cursor()
        query = """
            SELECT album.id_album, album.titre, album.annee_sortie, album.pochette, artiste.nom
            FROM album
            INNER JOIN artiste_album
            ON artiste_album = album.id_album
            INNER JOIN artiste
            ON artiste.id_artiste = artiste_album.id_artiste
        """
        cursor.execute(query)
        albums = cursor.fetchall()
        for album in cast(list[tuple[int,str,int,Path|None,str]],albums):
            album_tmp = Album(id=album[0],name=album[1],release_year=album[2],cover_path=album[3])  
        if albums != []:
            albums_tmp = []
            for album in cast(list[tuple[int,str,int,Path|None,str]],albums):
                if albums_tmp == []:
                    album_tmp = Album(
                        id=album[0],
                        name=album[1],
                        release_year=album[2],
                        cover_path=Path(album[3]) if album[3] is not None else None,
                        artists=[album[4]]
                    )
                    albums_tmp.append(album_tmp)
                else:
                    for album_tmp in albums_tmp:
                        if album[0] == album_tmp.id:
                            album_tmp.artist.append(album[4])
                            break
                    else:
                        album_tmp = Album(
                            id=album[0],
                            name=album[1],
                            release_year=album[2],
                            cover_path=Path(album[3]) if album[3] is not None else None,
                            artists=[album[4]]
                        )
                        albums_tmp.append(album_tmp)
            albums = albums_tmp
        cursor.close()
        cnx.close()
        return albums
    
    
    def find_by_name(self, titre:str)->Album|None:
        cnx = connect()
        cursor = cnx.cursor()
        query = """
            SELECT album.id_album, album.titre, album.annee_sortie, album.pochette, artiste.nom
            FROM album
            INNER JOIN artiste_album
            ON artiste_album.id_album = album.id_album
            INNER JOIN artiste
            ON artiste.id_artiste = artiste_album.id_artiste
            WHERE album.titre=%s
        """
        cursor.execute(query, (titre,))
        resultat = cursor.fetchall()
        if resultat:
            album_tmp = None
            for album in cast(list[tuple[int,str,int,Path|None,str]],resultat):
                if album_tmp is None:
                    album_tmp = Album(
                        id=album[0],
                        name=album[1],
                        release_year=album[2],
                        cover_path=Path(album[3]) if album[3] is not None else None, 
                        artists =[album[4]]
                    )
                else:
                    album_tmp.artists.append(album[4])
            else:
                album = album_tmp
        else:
            album = None
        cursor.close()
        cnx.close()
        return album

    def find_by_id(self, id:int)->Album|None:
        cnx = connect()
        cursor = cnx.cursor()
        query = """
            SELECT album.id_album, album.titre, album.annee_sortie, album.pochette, artiste.nom
            FROM album
            INNER JOIN artiste_album
            ON artiste_album = album.id_album
            INNER JOIN artiste
            ON artiste.id_artiste = artiste_album.id_artiste
            WHERE album.id_album=%s
        """
        cursor.execute(query, (id,))
        resultat = cursor.fetchall()
        if resultat:
            album_tmp = None
            for album in cast(list[tuple[int,str,int,Path|None,str]],resultat):
                if album_tmp is None:
                    album_tmp = Album(
                        id=album[0],
                        name=album[1],
                        release_year=album[2],
                        cover_path=Path(album[3]) if album[3] is not None else None, 
                        artists =[album[4]]
                    )
                else:
                    album_tmp.artists.append(album[4])
            else:
                album = album_tmp
        else:
            album = None
        cursor.close()
        cnx.close()
        return album
    

    def update_cover(self, id_album:int, cover_path=None):
        cnx = connect()
        cursor = cnx.cursor()
        query = """
            UPDATE album
            SET pochette = %s
            WHERE id_album = %s
        """
        cursor.execute(query, (str(cover_path), id_album))
        cnx.commit()
        cursor.close()
        cnx.close()


album_repository = AlbumRepository()