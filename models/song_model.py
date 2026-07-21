from dataclasses import dataclass
from pathlib import Path
from models.artist_model import Artist
from models.album_model import Album
from models.directory_model import Directory
from typing import Optional
@dataclass
class Song:
    id: Optional[int] = None
    title: str = ""
    artist: Optional[list[Artist]] = None
    album: Optional[Album] = None
    genre: Optional[str] = None
    path: Optional[Path] = None
    directory: Optional[Directory] = None