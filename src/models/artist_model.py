from dataclasses import dataclass

@dataclass
class Artist: 

    id: int 
    name: str = ""

    def to_dict(self)->dict:
        return {
            "name": self.name
        }