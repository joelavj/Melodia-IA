from pathlib import Path

class FileScanner:

    def mp3(self, path:Path)->list:
            return list(path.rglob('*.mp3'))


file_scanner = FileScanner()