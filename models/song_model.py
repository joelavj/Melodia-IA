from dataclasses import dataclass, field
from pathlib import Path
from models.artist_model import Artist
from models.album_model import Album
from models.directory_model import Directory
from typing import Optional

@dataclass
class Song:
    id: Optional[int] = -1
    title: Optional[str] = ""
    artist: Optional[list[Artist]] = field(default_factory=list)
    album: Optional[Album] = field(default_factory=Album)
    genre: Optional[str] = ""
    directory: Optional[Directory] = field(default_factory=Directory)
    path: Optional[Path] = None