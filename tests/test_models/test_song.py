import unittest
from src.models.song import Song

class TestSong(unittest.TestCase):
    def setUp(self):
        self.song = Song(title="Test Song", artist="Test Artist", duration=210)

    def test_song_creation(self):
        self.assertEqual(self.song.title, "Test Song")
        self.assertEqual(self.song.artist, "Test Artist")
        self.assertEqual(self.song.duration, 210)

    def test_song_duration(self):
        self.song.duration = 300
        self.assertEqual(self.song.duration, 300)

    def test_song_repr(self):
        self.assertEqual(repr(self.song), "Song(title='Test Song', artist='Test Artist', duration=210)")

if __name__ == "__main__":
    unittest.main()