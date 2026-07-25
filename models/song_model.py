from dataclasses import dataclass
from pathlib import Path
from models.artist_model import Artist
from models.album_model import Album
from models.directory_model import Directory
from typing import Optional
@dataclass
class Song:
    id: int = -1
    title: str = ""
    artist: list[Artist] = []
    album: Album = Album()
    genre: str = ""
    path: Optional[Path] = None
    directory: Directory = Directory()