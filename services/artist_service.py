import repositories.artist_repository as artist_repository
from models.artist_model import Artist

def is_empty(id:int)->bool:
    if artist_repository.get_songs(id) == [] and artist_repository.get_albums(id) == []:
        return True
    return False
    
def load_artists()->list[Artist]:
    artists = []
    for artist in artist_repository.find_all():
        if isinstance(artist.id, int) and isinstance(artist.name, str):
            if is_empty(artist.id):
                artist_repository.delete(artist.id)
            else:
                artists.append(Artist(id=artist.id, name=artist.name))
    return artists