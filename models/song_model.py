from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional
from models.directory_model import Directory

@dataclass
class Song:
    directory: Directory
    id: Optional[int] = -1
    title: Optional[str] = ""
    artist: Optional[list[str]] = field(default_factory=list)
    album: Optional[str] = ""
    genre: Optional[str] = ""
    path: Optional[Path] = None
    release_year: Optional[int] = -1

