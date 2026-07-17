from pathlib import Path
import repositories.song_repository as song_repository
import repositories.album_repository as album_repository
import repositories.artiste_repository as artiste_repository

def isSongStored(path:Path)->bool:
    if song_repository.findByPath(path) == []:
        return False
    else:
        return True
    
def add(data:dict, path:Path, id_repertoire:int):
    # Ajout de l'album ou récupération si déjà existant
    tmp = album_repository.findByName(data['album'])
    if tmp == []:
        id_album = album_repository.save(data['album'], data['annee'])
    else:
        id_album = tmp[0][0]

    # Ajout et liaison des artistes de l'album
    for nom_artiste in data['artistes_album']:
        tmp = artiste_repository.findByName(nom_artiste)
        if tmp == []:
            id_artiste = artiste_repository.save(nom_artiste)
        else:
            id_artiste = tmp[0][0]
        artiste_repository.link_album(id_artiste, id_album)

    # Ajout du morceau si nécessaire, sinon récupération de son id
    existing_song = song_repository.findByPath(path)
    if existing_song == []:
        id_morceau = song_repository.save(data['titre'], path, data['genre'], id_repertoire, id_album)
    else:
        id_morceau = existing_song[0][0]

    # Ajout et liaison des artistes du morceau
    for nom_artiste in data['artistes_morceau']:
        tmp = artiste_repository.findByName(nom_artiste)
        if tmp == []:
            id_artiste = artiste_repository.save(nom_artiste)
        else:
            id_artiste = tmp[0][0]
        artiste_repository.link_morceau(id_artiste, id_morceau)

    
        

