import unittest
from src.controllers.player_controller import PlayerController

class TestPlayerController(unittest.TestCase):
    def setUp(self):
        self.controller = PlayerController()

    def test_play(self):
        self.controller.play()
        self.assertTrue(self.controller.is_playing)

    def test_pause(self):
        self.controller.play()  # Start playing
        self.controller.pause()
        self.assertFalse(self.controller.is_playing)

    def test_next(self):
        current_song = self.controller.current_song
        self.controller.next()
        self.assertNotEqual(current_song, self.controller.current_song)

    def test_previous(self):
        current_song = self.controller.current_song
        self.controller.previous()
        self.assertNotEqual(current_song, self.controller.current_song)

    def test_volume_change(self):
        initial_volume = self.controller.volume
        self.controller.change_volume(0.5)
        self.assertNotEqual(initial_volume, self.controller.volume)

if __name__ == '__main__':
    unittest.main()