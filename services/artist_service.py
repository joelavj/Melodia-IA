import repositories.artist_repository as artist_repository
from models.artist_model import Artist

def is_empty(id:int)->bool:
    if artist_repository.get_songs(id) == [] and artist_repository.get_albums(id) == []:
        return True
    return False
    
def load_artists()->list[Artist]:
    for artiste in artist_repository.find_all():
        if is_empty(artiste[0]):
            artist_repository.delete(artiste[0])
    artists = []
    for artist in artist_repository.find_all():
        if is_empty(artist[0]):
            artist_repository.delete(artist[0])
        else:
            artists.append(Artist(id=artist[0], name=artist[1]))
    return artists