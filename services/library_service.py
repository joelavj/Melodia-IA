import services.album_service as album_service
import services.artist_service as artist_service
import services.song_service as song_service
import services.directory_service as directory_service

def load_library()->list[dict]:
    library = []
    library.append({"directories": directory_service.load_directories()})
    library.append({"songs": song_service.load_songs()})
    library.append({"albums": album_service.load_albums()})
    library.append({"artistes": artist_service.load_artists()})
    return library
