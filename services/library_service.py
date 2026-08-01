import services.song_service as song_service
import services.directory_service as directory_service
import services.queue_service as queue_service

def load_library():
    return {
        'directories': directory_service.load_directories(),
        'songs': song_service.load_songs(),
        'queue': queue_service.load_queue()
    }