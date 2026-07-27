from pathlib import Path
import repositories.song_repository as song_repository
import repositories.album_repository as album_repository
import repositories.artist_repository as artist_repository
import repositories.directory_repository as directory_repository
from models.album_model import Album
from models.song_model import Song
from models.artist_model import Artist
from models.directory_model import Directory
from typing import cast

def is_song_stored(path:Path)->bool:
    if song_repository.find_by_path(path) == []:
        return False
    else:
        return True
    
def add_song(data:dict, path:Path, id_repertoire:int):
    # Ajout de l'album ou récupération si déjà existant
    album = album_repository.find_by_name(data['album'])
    if album is not None and isinstance(album.id, int):
        id_album = album.id
    else:
        id_album = album_repository.save(data['album'], data['annee'])
    # Ajout et liaison des artistes de l'album
    for nom_artiste in data['artistes_album']:
        artist_row = artist_repository.find_by_name(nom_artiste)
        if artist_row is not None and isinstance(artist_row.id, int):
            id_artiste = artist_row.id
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
        if artist_row is not None and isinstance(artist_row.id, int):
            id_artiste = artist_row.id
        else:
            id_artiste = artist_repository.save(nom_artiste)
        artist_repository.link_morceau(id_artiste, id_morceau)

def delete_song(id:int)->None:
    song_repository.delete(id)

def load_songs()->list:
    songs = []
    for song in song_repository.find_all():
        song_id = song.id
        if isinstance(song_id, int) and isinstance(song.path, Path):
            if not Path(song.path).exists():
                song_repository.delete(song_id)
                continue
            if isinstance(song.album, Album) and isinstance(song.album.id, int):
                album_row = album_repository.find_by_id(song.album.id)
                if album_row is not None:
                    song.album = album_row
            artists = []
            for artist in song_repository.get_artists(song_id):
                artists.append(artist)
            song.artist = artists
            songs.append(song)
    return songs
        