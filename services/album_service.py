import repositories.album_repository as album_repository
import repositories.artist_repository as artist_repository
from models.artist_model import Artist
from models.album_model import Album


def is_empty(id: int) -> bool:
    return len(album_repository.get_songs(id)) == 0


def load_albums()->list[Album]:
    albums = []
    for album in album_repository.find_all():
        album_id = int(album[0])
        if is_empty(album_id):
            album_repository.delete(album_id)
            continue

        artists = []
        for artist in album_repository.get_artists(album_id):
            artist_id = int(artist[0]) if isinstance(artist, (tuple, list)) else int(artist)
            artist_row = artist_repository.find_by_id(artist_id)
            artist_name = None

            if isinstance(artist_row, (tuple, list)) and len(artist_row) > 1:
                artist_name = str(artist_row[1])
            elif isinstance(artist_row, dict):
                artist_name = str(artist_row.get("nom", ""))

            if artist_name:
                artists.append(Artist(id=artist_id, name=artist_name))

        albums.append(
            Album(
                id=album_id,
                title=str(album[1]),
                artist=artists,
                release_year=int(album[2]),
            )
        )
    return albums
