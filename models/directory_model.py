from dataclasses import dataclass
from pathlib import Path
from typing import Optional

@dataclass
class Directory:
    id:int
    path: Path