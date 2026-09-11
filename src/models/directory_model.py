from pathlib import Path

class Directory:
    def __init__(self, id:int, path:str):
        self.id = id
        self.path = Path(path)