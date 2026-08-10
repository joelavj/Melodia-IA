from dataclasses import field
from pathlib import Path
from typing import Optional
from models.directory_model import Directory
from models.album_model import Album
from models.artist_model import Artist

class Song:
    def __init__(self, path:Path, directory:Directory, id:int=-1,title:str="",artists:list[Artist]=field(default_factory=list),album:Optional[Album]=None,genre:str="") -> None:
        self.directory:Directory = directory    
        self.id:int = id
        self.title: str = title
        self.artists: list[Artist] = artists
        self.album: Album|None = album
        self.genre: str = genre
        self.path:Path = Path(path)

