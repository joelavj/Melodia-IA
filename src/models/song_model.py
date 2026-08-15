from pathlib import Path
from dataclasses import dataclass

@dataclass
class Song:

    id:int
    path: Path
    title: str = ""
    artists: str = ""
    album: str = ""
    cover_path: Path|None = None
    genre: str = ""

    def to_dict(self)->dict:
        return {
            "title": self.title,
            "album": self.album,
            "artists": self.artists,
            "genre": self.genre,
            "cover_path": self.cover_path
        }
