import os
from pathlib import Path

class CoverStorage :
    def __init__(self) -> None:
        self._path_storage = "cover_storage"
        if not os.path.exists(self._path_storage):
            os.mkdir(self._path_storage)

    def save(self, cover_data)->Path:
        numbers = []
        for file in os.listdir(self._path_storage):
            name_file, _ = os.path.splitext(file)
            if name_file.isdigit():
                numbers.append(int(name_file))
        else:
            if numbers:
                last_number = max(numbers)
                cover_name = str(last_number + 1)
            else:
                cover_name = "00"
        cover_path = os.path.join(self._path_storage, f"{cover_name}.{cover_data["ext"]}")
        with open(cover_path,"wb") as img_file:
            img_file.write(cover_data["data"])
        return Path(cover_path)

    def delete(self, cover_path:Path):
        os.remove(str(cover_path))

cover_storage = CoverStorage()