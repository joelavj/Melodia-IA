from pathlib import Path
from typing import cast
from models.song_model import SongSummary
from models.directory_model import Directory
from repositories.song_repository import song_repository
from repositories.album_repository import album_repository
from repositories.artist_repository import artist_repository
from infrastructure.cover_storage import cover_storage

class SongService :

    def is_here(self, path:Path)->bool:
        if isinstance(song_repository.short_find_by_path(path), SongSummary):
            return True
        return False


    def is_exist(self, path:Path)->bool:
        return Path(path).exists()


    # Ajout d'une musique complète à partir d'un morceau
    def add(self, data:dict, id_repertoire:int):
        # Ajout de l'album ou récupération si déjà existant
        album = album_repository.find_by_name(data['album'])
        if album is not None:
            id_album = album.id
        else:
            if data['cover'] is not None:
                data['cover'] = cover_storage.save(data['cover'])
            id_album = album_repository.save(data['album'], data['annee'],data['cover'])
            if id_album == False:
                return False
        # Ajout et liaison des artistes de l'album
        for nom_artiste in data['artistes_album']:
            artist_row = artist_repository.find_by_name(nom_artiste)
            if artist_row is not None:
                id_artiste = artist_row.id
            else:
                id_artiste = artist_repository.save(nom_artiste)
                if id_artiste == False:
                    return False
            artist_repository.link_album(id_artiste, id_album)
        # Ajout du morceau si nécessaire, sinon récupération de son id
        existing_song = song_repository.short_find_by_path(data['path'])
        if existing_song is not None:
            id_morceau = existing_song.id
        else:
            id_morceau = song_repository.save(data['titre'], data['path'], data['genre'], id_repertoire, id_album,data["duration"])
            if id_morceau == False:
                return False
        # Ajout et liaison des artistes du morceau
        for nom_artiste in data['artistes_morceau']:
            artist_row = artist_repository.find_by_name(nom_artiste)
            if artist_row is not None:
                id_artiste = artist_row.id
            else:
                id_artiste = artist_repository.save(nom_artiste)
            artist_repository.link_morceau(id_artiste, id_morceau)

    
    def remove(self, id:int)->bool:
        if song_repository.short_find_by_id(id) is not None:
            return song_repository.delete(id)
        return False

song_service = SongService()