from dataclasses import dataclass
from pathlib import Path
from typing import Optional
@dataclass
class Directory:
    id: Optional[int] = None
    path: Optional[Path] = None