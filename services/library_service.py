from models.directory_model import Directory
import services.album_service as album_service
import services.artist_service as artist_service
import services.song_service as song_service
import services.directory_service as directory_service
import services.queue_service as queue_service

def load_library()->dict:
    library = {}
    library["directories"] = directory_service.load_directories()
    library["songs"] = song_service.load_songs()
    library["albums"] = album_service.load_albums()
    library["artistes"] = artist_service.load_artists()
    queue_service.load_queue()
    return library

