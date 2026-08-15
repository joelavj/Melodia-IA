import unittest
from src.services.import_service import ImportService

class TestImportService(unittest.TestCase):

    def setUp(self):
        self.import_service = ImportService()

    def test_import_song(self):
        # Test d'importation d'une chanson
        result = self.import_service.import_song("path/to/song.mp3")
        self.assertTrue(result)
        # Ajoutez des assertions supplémentaires pour vérifier l'état après l'importation

    def test_import_playlist(self):
        # Test d'importation d'une playlist
        result = self.import_service.import_playlist("path/to/playlist.m3u")
        self.assertTrue(result)
        # Ajoutez des assertions supplémentaires pour vérifier l'état après l'importation

    def test_import_invalid_file(self):
        # Test d'importation d'un fichier invalide
        with self.assertRaises(ValueError):
            self.import_service.import_song("path/to/invalid_file.txt")

if __name__ == "__main__":
    unittest.main()