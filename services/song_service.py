from pathlib import Path
import repositories.song_repository as song_repository
import repositories.album_repository as album_repository
import repositories.artist_repository as artist_repository

def is_song_stored(path:Path)->bool:
    if song_repository.find_by_path(path) == []:
        return False
    else:
        return True
    
def add_song(data:dict, path:Path, id_repertoire:int):
    # Ajout de l'album ou récupération si déjà existant
    tmp = album_repository.find_by_name(data['album'])
    if tmp == []:
        id_album = album_repository.save(data['album'], data['annee'])
    else:
        id_album = tmp[0][0]

    # Ajout et liaison des artistes de l'album
    for nom_artiste in data['artistes_album']:
        tmp = artist_repository.findByName(nom_artiste)
        if tmp == []:
            id_artiste = artist_repository.save(nom_artiste)
        else:
            id_artiste = tmp[0][0]
        artist_repository.link_album(id_artiste, id_album)

    # Ajout du morceau si nécessaire, sinon récupération de son id
    existing_song = song_repository.find_by_path(path)
    if existing_song == []:
        id_morceau = song_repository.save(data['titre'], path, data['genre'], id_repertoire, id_album)
    else:
        id_morceau = existing_song[0][0]

    # Ajout et liaison des artistes du morceau
    for nom_artiste in data['artistes_morceau']:
        tmp = artist_repository.findByName(nom_artiste)
        if tmp == []:
            id_artiste = artist_repository.save(nom_artiste)
        else:
            id_artiste = tmp[0][0]
        artist_repository.link_morceau(id_artiste, id_morceau)

def delete_song(id:int)->None:
    song_repository.delete(id)

def load_songs()->list:
    for song in song_repository.find_all():
        if not Path(song[2]).exists():
            song_repository.delete(song[0])
    return song_repository.find_all()
        