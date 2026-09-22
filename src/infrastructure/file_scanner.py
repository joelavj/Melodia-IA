from pathlib import Path
from infrastructure.metadata.audio_reader import SUPPORTED_EXTENSIONS

class FileScanner:

    def audio(self, path: Path) -> list:
        """Retourne tous les fichiers audio d'un répertoire (et ses
        sous-répertoires), quel que soit leur format, parmi ceux pris en
        charge par l'application (cf. ``SUPPORTED_EXTENSIONS``).
        """
        files = []
        for extension in SUPPORTED_EXTENSIONS:
            files.extend(path.rglob(f'*{extension}'))
            files.extend(path.rglob(f'*{extension.upper()}'))
        # Dédoublonne (utile sur les systèmes de fichiers insensibles à la casse)
        return list(dict.fromkeys(files))

    def mp3(self, path: Path) -> list:
        """Conservé pour compatibilité ascendante : ne renvoie que les MP3."""
        return list(path.rglob('*.mp3')) + list(path.rglob('*.MP3'))


file_scanner = FileScanner()
