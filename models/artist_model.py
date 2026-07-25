from dataclasses import dataclass
from pathlib import Path
from typing import Optional
@dataclass
class Artist:
    id: int = -1
    name: str = ""