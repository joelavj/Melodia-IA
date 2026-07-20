import repositories.artist_repository as artist_repository

def is_empty(id:int)->bool:
    if artist_repository.get_songs(id) == [] and artist_repository.get_albums(id) == []:
        return True
    return False
    
def load_artists():
    for artiste in artist_repository.find_all():
        if is_empty(artiste[0]):
            artist_repository.delete(artiste[0])
    return artist_repository.find_all()
    