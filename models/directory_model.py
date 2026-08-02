from pathlib import Path
from typing import Any

class Directory:

    def __init__(self, id:int, path:Path) -> None:
        self.id = id
        self.path = Path(path)
