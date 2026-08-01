from dataclasses import dataclass, field
from pathlib import Path
from models.artist_model import Artist
from typing import Optional, List
@dataclass      
class Album:
    id: Optional[int] = None
    title: str = ""
    artist: list = field(default_factory=list)
    release_year: Optional[int] = None