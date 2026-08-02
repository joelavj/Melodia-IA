from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional
from models.directory_model import Directory

@dataclass
class Song:
<<<<<<< HEAD
    """id: int = -1
    title: str = ""
    artist: list[Artist] = []
    album: Album = Album()
    genre: str = ""
    path: Optional[Path] = None
    directory: Directory = Directory()"""
    id: int = -1
    title: str = ""
    artist: list[Artist] = field(default_factory=list)
    album: Album = field(default_factory=Album)
    genre: str = ""
    path: Optional[Path] = None
    directory: Directory = field(default_factory=Directory)
=======
    id: Optional[int] = -1
    title: Optional[str] = ""
    artist: Optional[list[str]] = field(default_factory=list)
    album: Optional[str] = ""
    genre: Optional[str] = ""
    directory: Optional[Directory] = field(default_factory=Directory)
    path: Optional[Path] = None
    release_year: Optional[int] = -1
>>>>>>> 435b7723e870beebedfec899b61cb68160bdd538
