from dataclasses import dataclass, field
from pathlib import Path
from models.artist_model import Artist
from typing import Optional

@dataclass      
class Album:
    id: Optional[int] = -1
    title: Optional[str] = ""
    artist: Optional[list[Artist]] = field(default_factory=list)
    release_year: Optional[int] = None