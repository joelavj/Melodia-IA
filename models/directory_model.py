from dataclasses import dataclass
from pathlib import Path
from typing import Optional
@dataclass
class Directory:
    id: Optional[int] = -1
    path: Optional[Path] = None