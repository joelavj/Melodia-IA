from pathlib import Path
from dataclasses import dataclass, field

@dataclass
class SongSummary:
    id: int
    title: str
    artists: str
    album: str
    duration: int
    favori: bool

class Song:
    def __init__(self,id:int,title:str,path:str,genre:str,artists:list[str],album:str,cover_path:str|None,duration:int,favori:int) -> None:
        self.id:int = id
        self.title:str = title
        self.path:Path = Path(path)
        self.artists:list[str] = artists
        self.album:str = album
        self.genre:str = genre
        self.cover_path:Path|None = Path(cover_path) if cover_path is not None else None
        self.duration:int = duration
        self.favori:bool = bool(favori)
