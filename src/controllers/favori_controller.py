from services.favori_service import favori_service

class FavoriController:
    def add_favori(self,id_song:int):
        favori_service.add_favori(id_song)

    def remove_favori(self, id_song:int):
        favori_service.remove_favori(id_song)

    def play(self,id_song:int|None):
        favori_service.play(id_song)

favori_controller = FavoriController()