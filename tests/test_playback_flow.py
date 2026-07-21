import sys
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import main
from controllers import queue_controller, player_controller
from models.artist_model import Artist
from models.song_model import Song
from services import queue_service, player_service
from utils.constante import StatePlay


class PlaybackFlowTests(unittest.TestCase):
    def setUp(self):
        queue_service.reset_queue()
        player_service.state_player = StatePlay.STOP

    def test_add_song_uses_active_queue(self):
        song = Song(id=1, title="Track 1", path=Path("/tmp/track1.mp3"))

        queue_controller.add_song(song)
        active_queue = queue_service.get_active_queue()

        self.assertEqual(active_queue.queue[-1].id, song.id)
        self.assertEqual(active_queue.current_song, None)

    def test_pause_changes_state_when_playing(self):
        song = Song(id=2, title="Track 2", path=Path("/tmp/track2.mp3"))
        queue_controller.add_song(song)

        player_controller.play(song)
        player_controller.pause()

        self.assertEqual(player_service.state_player, StatePlay.PAUSE)

    def test_play_without_song_uses_active_queue(self):
        song = Song(id=3, title="Track 3", path=Path("/tmp/track3.mp3"))
        queue_controller.add_song(song)

        player_controller.play()

        active_queue = queue_service.get_active_queue()
        self.assertEqual(active_queue.current_song.id, song.id)

    def test_remove_song_updates_queue(self):
        first = Song(id=4, title="Track 4", path=Path("/tmp/track4.mp3"))
        second = Song(id=5, title="Track 5", path=Path("/tmp/track5.mp3"))
        queue_controller.add_song(first)
        queue_controller.add_song(second)

        queue_controller.remove_song(queue_service.get_active_queue(), first)

        active_queue = queue_service.get_active_queue()
        self.assertEqual(len(active_queue.queue), 1)
        self.assertEqual(active_queue.queue[0].id, second.id)

    def test_format_artists_handles_artist_objects(self):
        artists = [Artist(name="Artist A"), Artist(name="Artist B")]
        self.assertEqual(main._format_artists(artists), "Artist A, Artist B")


if __name__ == "__main__":
    unittest.main()
