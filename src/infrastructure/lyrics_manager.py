import re
from pathlib import Path
from typing import Literal, Sequence

from infrastructure.ai.lyrics_aligner import estimate_line_timestamps, LyricsAlignmentError


class LyricsManager:
    _timestamp_pattern = re.compile(r"\[(?P<minutes>\d+):(?P<seconds>\d{1,2})(?:\.(?P<milliseconds>\d{1,3}))?\](?P<text>.*)")

    def __init__(self) -> None:
        self.lyrics_storage = Path(__file__).resolve().parents[1] / "tmp/lyrics_storage/"
        self.lyrics_storage.mkdir(parents=True, exist_ok=True)

    def new_file(self) -> Path:
        existing_files = [
            path for path in self.lyrics_storage.iterdir()
            if path.is_file() and path.suffix.lower() == ".lrc"
        ]
        numbers = []
        for path in existing_files:
            try:
                numbers.append(int(path.stem))
            except ValueError:
                continue
        if numbers:
            name_file = f"{max(numbers) + 1}.lrc"
        else:
            name_file = "00.lrc"
        path_lyrics = self.lyrics_storage / name_file
        path_lyrics.touch(exist_ok=True)
        return path_lyrics

    def delete_file(self, path: Path):
        if path.exists():
            path.unlink()

    def import_file(self, path: str | Path) -> list[str]:
        file_path = Path(path)
        if not file_path.exists():
            raise FileNotFoundError(f"Fichier de paroles introuvable: {file_path}")

        with open(file_path, "r", encoding="utf-8") as file:
            lines = file.read().splitlines()
        return [line.strip() for line in lines if line.strip()]

    def edit_lines(self, content: Sequence[str] | str | None, edited_lines: Sequence[str]) -> list[str]:
        current_lines = content.splitlines() if isinstance(content, str) else list(content or [])
        if not current_lines and edited_lines:
            current_lines = list(edited_lines)
        else:
            if len(current_lines) == len(edited_lines):
                current_lines = list(edited_lines)
            elif len(edited_lines) >= len(current_lines):
                current_lines = list(edited_lines)
            else:
                current_lines[:len(edited_lines)] = edited_lines
        return [line.strip() for line in current_lines if line.strip()]

    def generate_manual_sync(self, content: Sequence[str] | str | None, timestamps: Sequence[float]) -> list[str]:
        lines = content.splitlines() if isinstance(content, str) else list(content or [])
        clean_lines = [line.strip() for line in lines if line.strip()]
        if not clean_lines:
            return []

        if len(timestamps) != len(clean_lines):
            raise ValueError("Le nombre de timestamps doit correspondre au nombre de lignes de paroles.")

        synced_lines = []
        for raw_line, timestamp in zip(clean_lines, timestamps):
            minutes, seconds = divmod(float(timestamp), 60)
            whole_seconds = int(seconds)
            hundredths = int(round((seconds - whole_seconds) * 100))
            if hundredths == 100:
                hundredths = 0
                whole_seconds += 1
            if whole_seconds == 60:
                whole_seconds = 0
                minutes += 1
            formatted = f"[{int(minutes):02d}:{whole_seconds:02d}.{hundredths:02d}] {raw_line}"
            synced_lines.append(formatted)
        return synced_lines

    def generate_automatic_sync(self, content: Sequence[str] | str | None, audio_path: Path) -> list[str]:
        """Génère automatiquement une synchronisation LRC à partir de
        paroles brutes (sans timestamps) et du fichier audio du morceau.

        Contrairement à ``generate_manual_sync``, aucun timestamp n'a besoin
        d'être fourni : ils sont estimés à partir du contenu audio (voir
        ``infrastructure/ai/lyrics_aligner.py`` pour la méthode utilisée et
        ses limites).
        """
        lines = content.splitlines() if isinstance(content, str) else list(content or [])
        clean_lines = [line.strip() for line in lines if line.strip()]
        if not clean_lines:
            return []

        timestamps = estimate_line_timestamps(clean_lines, audio_path)
        return self.generate_manual_sync(clean_lines, timestamps)

    def modify_file(self, path: Path, content: Sequence[str] | str | None) -> bool:
        if path is None or not path.exists():
            return False
        if content is None:
            content = []
        if isinstance(content, str):
            content = content.splitlines()
        with open(path, "w", encoding="utf-8") as file:
            file.writelines(line if line.endswith("\n") else f"{line}\n" for line in content)
        return True

    def read_file(self, path: Path) -> list[str] | Literal[False]:
        if path is None or not path.exists():
            return False
        with open(path, "r", encoding="utf-8") as file:
            return file.readlines()

    def parse_lrc(self, content: Sequence[str] | str | None) -> list[dict[str, float | str]]:
        if content is None:
            return []
        lines = content.splitlines() if isinstance(content, str) else list(content)
        parsed: list[dict[str, float | str]] = []

        for raw_line in lines:
            clean = raw_line.strip()
            if not clean:
                continue
            match = self._timestamp_pattern.match(clean)
            if match is None:
                continue
            minutes = int(match.group("minutes"))
            seconds = int(match.group("seconds"))
            milliseconds = match.group("milliseconds")
            if milliseconds is not None:
                seconds += int(milliseconds) / (10 ** len(milliseconds))
            time = minutes * 60 + seconds
            text = match.group("text").strip()
            parsed.append({"time": round(float(time), 3), "text": text})

        parsed.sort(key=lambda item: float(item["time"]))
        return parsed

    def get_current_lyric(self, content: Sequence[str] | str | None, current_time: float) -> str:
        lines = self.parse_lrc(content)
        if not lines:
            return ""

        current_time = float(current_time)
        first = lines[0]
        last = lines[-1]

        if current_time <= float(first["time"]):
            return str(first["text"])

        for i, line in enumerate(lines[:-1]):
            next_line = lines[i + 1]
            if float(line["time"]) <= current_time < float(next_line["time"]):
                return str(line["text"])

        return str(last["text"]) if current_time >= float(last["time"]) else ""


lyrics_manager = LyricsManager()