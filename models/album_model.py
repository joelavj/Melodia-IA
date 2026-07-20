from dataclasses import dataclass
from pathlib import Path
@dataclass      
class Album:
    id: int
    title: str
    artist: list[str]
    release_year: int