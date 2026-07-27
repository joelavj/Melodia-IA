from dataclasses import dataclass
from pathlib import Path
from typing import Optional
@dataclass
class Artist:
    id: Optional[int] = -1
    name: Optional[str] = ""