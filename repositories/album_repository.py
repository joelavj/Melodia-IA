from database.connect import connect
from typing import cast
from pathlib import Path
from typing import Optional
from models.album_model import Album
from models.artist_model import Artist

class AlbumRepository :

    def save(self, titre:str, annee_sortie:str, cover_path:Optional[Path]=None)->int:
        titre = titre.strip() if titre else ""
        if not titre:
            titre = "inconnu"
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
        return int(lastrowid) if lastrowid is not None else 0


    def link_artiste(self, id_artiste:int, id_album:int):
        cnx = connect()
        cursor = cnx.cursor()
        query = """
            INSERT INTO artiste_album(id_artiste, id_album) 
            VALUES (%s, %s)
        """
        cursor.execute(query, (id_artiste, id_album))
        cnx.commit()
        cursor.close()
        cnx.close()

    def find_all(self)->list:
        cnx = connect()
        cursor = cnx.cursor()
        query = """
            SELECT album.id_album, album.titre, album.annee_sortie, album.pochette, artiste.id, artiste.nom
            FROM album
            INNER JOIN artiste_album
            ON artiste_album.id_album = album.id_album
            INNER JOIN artiste
            ON artiste.id_artiste = artiste_album.id_artiste
        """
        cursor.execute(query)
        resultat = cursor.fetchall()
        if resultat:
            albums_tmp = []
            for album in cast(list[tuple[int,str,int,Path|None,int,str]],resultat):
                if albums_tmp == []:
                    albums_tmp.append(Album(
                        id=album[0],
                        name=album[1],
                        release_year=album[2],
                        cover_path=album[3],
                        artists=[Artist(
                            id=album[4],
                            name=album[5]
                        )]
                    ))
                else:
                    for album_tmp in albums_tmp:
                        if album_tmp.id == album[0]:
                            album_tmp.artists.append(Artist(
                                id=album[4],
                                name=album[5]
                            ))
                            break
                    else:
                        albums_tmp.append(Album(
                            id=album[0],
                            name=album[1],
                            release_year=album[2],
                            cover_path=album[3],
                            artists=[Artist(
                                id=album[4],
                                name=album[5]
                            )]
                        ))

            else:
                albums = albums_tmp
        else:
            albums = []

        cursor.close()
        cnx.close()
        return albums
    
    
    def find_by_name(self, titre:str)->Album|None:
        cnx = connect()
        cursor = cnx.cursor()
        query = """
            SELECT album.id_album, album.titre, album.annee_sortie, album.pochette, artiste.id, artiste.nom
            FROM album
            INNER JOIN artiste_album
            ON artiste_album.id_album = album.id_album
            INNER JOIN artiste
            ON artiste.id_artiste = artiste_album.id_artiste
            WHERE album.titre=%s
        """
        cursor.execute(query, (titre,))
        resultat = cursor.fetchall()
        album = None
        if resultat:
            for album_tmp in cast(list[tuple[int,str,int,Path|None,int,str]],resultat):
                if album is None:
                    album = Album(
                        id=album_tmp[0],
                        name=album_tmp[1],
                        release_year=album_tmp[2],
                        cover_path=album_tmp[3],
                        artists=[Artist(
                            id=album_tmp[4],
                            name=album_tmp[5]
                        )]
                    )
                else:
                    album.artists.append(Artist(
                        id=album_tmp[4],
                        name=album_tmp[5]
                    ))
        cursor.close()
        cnx.close()
        return album


    def find_by_id(self, id:int)->Album|None:
        cnx = connect()
        cursor = cnx.cursor()
        query = """
            SELECT album.id_album, album.titre, album.annee_sortie, album.pochette, artiste.id, artiste.nom
            FROM album
            INNER JOIN artiste_album
            ON artiste_album.id_album = album.id_album
            INNER JOIN artiste
            ON artiste.id_artiste = artiste_album.id_artiste
            WHERE album.id_album=%s
        """
        cursor.execute(query, (id,))
        resultat = cursor.fetchall()
        album = None
        if resultat:
            for album_tmp in cast(list[tuple[int,str,int,Path|None,int,str]],resultat):
                if album is None:
                    album = Album(
                        id=album_tmp[0],
                        name=album_tmp[1],
                        release_year=album_tmp[2],
                        cover_path=album_tmp[3],
                        artists=[Artist(
                            id=album_tmp[4],
                            name=album_tmp[5]
                        )]
                    )
                else:
                    album.artists.append(Artist(
                        id=album_tmp[4],
                        name=album_tmp[5]
                    ))
        cursor.close()
        cnx.close()
        return album


album_repository = AlbumRepository()