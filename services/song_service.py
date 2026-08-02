from pathlib import Path
from typing import cast
from models.song_model import Song
from models.directory_model import Directory
from repositories.song_repository import song_repository
from repositories.album_repository import album_repository
from repositories.artist_repository import artist_repository

class SongService :

    def is_stored(self, path:Path)->bool:
        if song_repository.find_by_path(path) is None:
            return False
        else:
            return True


    def is_exist(self, path:Path)->bool:
        return Path(path).exists()


    def add(self, data:dict, path:Path, id_repertoire:int):
        # Ajout de l'album ou récupération si déjà existant
        album = album_repository.find_by_name(data['album'])
        if album is not None:
            id_album = album["id"]
        else:
            id_album = album_repository.save(data['album'], data['annee'])
        # Ajout et liaison des artistes de l'album
        for nom_artiste in data['artistes_album']:
            artist_row = artist_repository.find_by_name(nom_artiste)
            if artist_row is not None:
                id_artiste = artist_row["id"]
            else:
                id_artiste = artist_repository.save(nom_artiste)
            artist_repository.link_album(id_artiste, id_album)
        # Ajout du morceau si nécessaire, sinon récupération de son id
        existing_song = song_repository.find_by_path(path)
        if existing_song is not None and isinstance(existing_song.id,int):
            id_morceau = int(existing_song.id)
        else:
            id_morceau = song_repository.save(data['titre'], path, data['genre'], id_repertoire, id_album)
        # Ajout et liaison des artistes du morceau
        for nom_artiste in data['artistes_morceau']:
            artist_row = artist_repository.find_by_name(nom_artiste)
            if artist_row is not None:
                id_artiste = artist_row["id"]
            else:
                id_artiste = artist_repository.save(nom_artiste)
            artist_repository.link_morceau(id_artiste, id_morceau)


    def delete(self, id:int)->None:
        song_repository.delete(id)


song_service = SongService()