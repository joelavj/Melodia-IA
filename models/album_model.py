from dataclasses import dataclass
from pathlib import Path
from models.artist_model import Artist
from typing import Optional
@dataclass      
class Album:
    id: int = -1
    title: str = ""
    artist: list[Artist] = []
    release_year: Optional[int] = None