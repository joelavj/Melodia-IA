import repositories.album_repository as album_repository

def is_empty(id:int)->bool:
    if album_repository.get_songs == []:
        return True
    else:
        return False
    
def load_albums():
    for album in album_repository.find_all():
        if is_empty(album[0]):
            album_repository.delete(album[0])
    return album_repository.find_all()
    
    