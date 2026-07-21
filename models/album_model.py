from dataclasses import dataclass
from pathlib import Path
from models.artist_model import Artist
@dataclass      
class Album:
    id: int
    title: str
    artist: list[Artist]
    release_year: int