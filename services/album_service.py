import repositories.album_repository as album_repository
import repositories.artist_repository as artist_repository
from models.artist_model import Artist
from models.album_model import Album


def is_empty(id: int) -> bool:
    return len(album_repository.get_songs(id)) == 0


def load_albums()->list[Album]:
    albums:list[Album] = []
    for album in album_repository.find_all():
        album_id = album.id
        if isinstance(album_id, int) and isinstance(album.title, str):
            artists:list[Artist] = []
            for artist in album_repository.get_artists(album_id):
                if isinstance(artist.id,int):
                    artist_row = artist_repository.find_by_id(artist.id)
                    artist_name =  None if artist_row is None else artist_row.name
                    if artist_name:
                        artists.append(Artist(id=artist.id, name=artist_name))
            albums.append(
                Album(
                    id= album_id,
                    title= album.title,
                    artist= artists,
                    release_year= album.release_year,
                )
            )
    return albums
