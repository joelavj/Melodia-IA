import os
from pathlib import Path

# Gère la pochette 
class CoverStorage :
    
    def __init__(self) -> None:
        self._path_storage = Path("tmp/cover_storage")
        self._path_storage.mkdir(parents=True,exist_ok=True)

    def save(self, cover_data)->Path:
        numbers = [int(path.stem) for path in self._path_storage.iterdir() if path.is_file() and path.stem.isdigit()]
        cover_ext = "png" if "png" in (cover_data.mime).lower() else "jpg"
        if numbers:
            name_file = f"{max(numbers) + 1}.{cover_ext}"
        else:
            name_file = f"00.{cover_ext}"
        cover_path = self._path_storage / name_file
        with open(cover_path,"wb") as img_file:
            img_file.write(cover_data.data)
        return cover_path

    def delete(self, cover_path:Path)->bool:
        if not cover_path.exists():
            return False
        cover_path.unlink()
        return True
        


cover_storage = CoverStorage()