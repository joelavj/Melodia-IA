from dataclasses import dataclass
from pathlib import Path
from models.artist_model import Artist
from typing import Optional
@dataclass      
class Album:
    id: Optional[int] = None
    title: Optional[str] = None
    artist: Optional[list[Artist]] = None
    release_year: Optional[int] = None