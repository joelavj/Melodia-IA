from typing import Optional
from pathlib import Path
from dataclasses import dataclass, field

@dataclass
class Album :
    id:int = -1
    name:str = ""
    cover_path: Optional[Path] = None
    artists: list[str] = field(default_factory=list)
    release_year: int = -1