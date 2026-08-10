from pathlib import Path
from dataclasses import field
from typing import Optional
from models.artist_model import Artist

class Album :
    def __init__(self, id:int=-1, name:str="", cover_path:Optional[Path]=None,artists:list[Artist]=field(default_factory=list), release_year:int=-1) -> None:
        self.id:int = id
        self.name:str = name
        self.cover_path:Path|None = Path(cover_path) if cover_path is not None else None
        self.artists:list = artists
        self.release_year:int = release_year
