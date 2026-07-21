from pathlib import Path
import repositories.song_repository as song_repository
import repositories.album_repository as album_repository
import repositories.artist_repository as artist_repository
from models.album_model import Album
from models.song_model import Song
from models.artist_model import Artist


def _get_first_value(row) -> int:
    if row is None:
        return 0
    if isinstance(row, (tuple, list)):
        return _safe_int(row[0])
    if isinstance(row, dict):
        return _safe_int(row.get("id_artiste", 0))
    return 0


def _safe_int(value) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return 0


def is_song_stored(path:Path)->bool:
    if song_repository.find_by_path(path) == []:
        return False
    else:
        return True
    
def add_song(data:dict, path:Path, id_repertoire:int):
    # Ajout de l'album ou récupération si déjà existant
    tmp = album_repository.find_by_name(data['album'])
    if not tmp:
        id_album = album_repository.save(data['album'], data['annee'])
    else:
        id_album = int(tmp[0][0])

    # Ajout et liaison des artistes de l'album
    for nom_artiste in data['artistes_album']:
        artist_row = artist_repository.find_by_name(nom_artiste)
        if not artist_row:
            id_artiste = artist_repository.save(nom_artiste)
        else:
            id_artiste = _get_first_value(artist_row)
        artist_repository.link_album(id_artiste, id_album)

    # Ajout du morceau si nécessaire, sinon récupération de son id
    existing_song = song_repository.find_by_path(path)
    if not existing_song:
        id_morceau = song_repository.save(data['titre'], path, data['genre'], id_repertoire, id_album)
    else:
        id_morceau = int(existing_song[0][0])

    # Ajout et liaison des artistes du morceau
    for nom_artiste in data['artistes_morceau']:
        artist_row = artist_repository.find_by_name(nom_artiste)
        if not artist_row:
            id_artiste = artist_repository.save(nom_artiste)
        else:
            id_artiste = _get_first_value(artist_row)
        artist_repository.link_morceau(id_artiste, id_morceau)

def delete_song(id:int)->None:
    song_repository.delete(id)

def load_songs()->list:
    songs = []
    for song in song_repository.find_all():
        song_id = int(song[0])
        if not Path(song[2]).exists():
            song_repository.delete(song_id)
            continue

        album_row = album_repository.find_by_id(song[3]) if len(song) > 3 else None
        album = {}
        if isinstance(album_row, (tuple, list)) and len(album_row) >= 2:
            album_id = _safe_int(album_row[0])
            album = {
                "id": album_id,
                "titre": str(album_row[1]),
            }
        elif isinstance(album_row, dict):
            album_id = _safe_int(album_row.get("id_album", 0))
            album = {
                "id": album_id,
                "titre": str(album_row.get("titre", "")),
            }

        artists = []
        for artist in song_repository.get_artists(song_id):
            artist_id = int(artist[0]) if isinstance(artist, (tuple, list)) else int(artist)
            artist_row = artist_repository.find_by_id(artist_id)
            if isinstance(artist_row, (tuple, list)) and len(artist_row) >= 2:
                artists.append(Artist(id=artist_id, name=str(artist_row[1])))
            elif isinstance(artist_row, dict):
                artists.append(Artist(id=artist_id, name=str(artist_row.get("nom", ""))))

        songs.append(
            Song(
                id=song_id,
                title=str(song[1]),
                artist=artists,
                album=album,
                genre=str(song[3]),
                path=Path(str(song[2])),
            )
        )
    return songs
        