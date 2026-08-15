from dataclasses import dataclass
from pathlib import Path

@dataclass
class Album:

    id: int
    title: str = ""
    cover_path: Path|None = None
    artists: str = ""
    release_year: int = 0

    def to_dict(self)->dict:
        return {
            "title": self.title,
            "artists": self.artists,
            "cover_path": self.cover_path,
            "release_year": self.release_year
        }