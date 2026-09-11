from pathlib import Path

class Album:
    def __init__(self,id:int,title:str,artists:str,release_year:int,cover_path:str|None=None):
        self.id = id
        self.title = title
        self.artists = artists
        self.release_year = release_year
        self.cover_path = Path(cover_path) if cover_path is not None else None