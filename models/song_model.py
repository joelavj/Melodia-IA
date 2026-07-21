from dataclasses import dataclass
from pathlib import Path
@dataclass
class Song:
    id: int
    title: str
    artist: list[str]
    album: dict
    genre: str
    path: Path