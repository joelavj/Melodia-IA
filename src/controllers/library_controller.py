from services.library_service import library_service

class LibraryController :
        
    def list_directories(self)->list:
        return library_service.list_directories()

    def list_songs(self)->list:
        return library_service.list_songs()

    def list_queue(self)->list:
        return library_service.list_queue()

    def list_artists(self)->list:
        return library_service.list_artists()

    def list_albums(self)->list:
        return library_service.list_albums()

    def list_playlists(self)->list:
        return library_service.list_playlists()

    def list_song_playlist(self,id_playlist:int)->list:
        return library_service.list_songs_playlist(id_playlist)

    def list_songs_album(self,id_album:int)->list:
        return library_service.list_songs_album(id_album)

    def info_song(self, id_song:int):
        return library_service.info_song(id_song)

    def list_favorite(self):
        return library_service.list_favorite()



library_controller = LibraryController()