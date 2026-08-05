from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional
from models.directory_model import Directory

@dataclass
class Song:
    directory: Directory
    id: int = -1
    title: str = ""
    artist: list[str] = field(default_factory=list)
    album: Optional[str] = ""
    genre: str = ""
    path: Optional[Path] = None
    release_year: int = -1

