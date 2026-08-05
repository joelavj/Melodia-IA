from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional
from models.directory_model import Directory
from models.album_model import Album

@dataclass
class Song:
    id: int = -1
    title: str = ""
    artists: list[str] = field(default_factory=list)
    genre: str = ""
    path: Optional[Path] = None
    album: Optional[Album] = None
    directory: Optional[Directory] = None

