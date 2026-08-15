from dataclasses import dataclass
from pathlib import Path

@dataclass
class Directory:

    id: int
    path: Path

    def to_dict(self)->dict:
        return {
            "directory": self.path
        }