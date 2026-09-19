from mutagen.id3 import ID3, ID3NoHeaderError
from mutagen.mp3 import MP3, HeaderNotFoundError
from mutagen import MutagenError
from pathlib import Path
from typing import Tuple, List
import re

class MetadataReader:

    _FEAT_KEYWORDS = r'(?:feat(?:uring)?|ft|featuring|with)\.?'

    def extract(self, path: Path) -> dict:
        """Extrait des métadonnées d'un fichier MP3 en gérant les fichiers sans header ID3.

        Retourne un dict avec les clés : titre, artistes_morceau, artistes_album,
        album, annee, genre, cover, path, duration.
        """
        path = Path(path)
        
        # 1. Chargement sécurisé des tags ID3
        try:
            audio = ID3(str(path))
        except (ID3NoHeaderError, MutagenError, Exception):
            audio = None

        # 2. Chargement sécurisé de la durée via MP3
        duration = 0.0
        try:
            mp3_file = MP3(str(path))
            if mp3_file.info:
                duration = mp3_file.info.length
        except (HeaderNotFoundError, MutagenError, Exception):
            duration = 0.0

        # Si aucun tag ID3 n'existe, on extrait les infos par défaut
        titre_raw = self._get_value(audio, 'TIT2') if audio else ""
        
        # Fallback : si pas de titre dans les tags ID3, utiliser le nom du fichier
        if not titre_raw:
            titre_raw = path.stem

        titre, title_feats = self._split_featuring(titre_raw)

        artiste_morceau_raw = self._get_value(audio, 'TPE1') if audio else ""
        artiste_album_raw = self._get_value(audio, 'TPE2') if audio else ""

        # Nettoyage et extraction des featuring depuis les champs artiste
        artiste_morceau, artist_feats1 = self._split_featuring(artiste_morceau_raw)
        artiste_album, artist_feats2 = self._split_featuring(artiste_album_raw)

        # Si artiste morceau manquant, utiliser artiste album
        if not artiste_morceau and artiste_album:
            artiste_morceau = artiste_album

        # Si les deux présents mais seulement différence de casse, harmoniser
        if artiste_morceau and artiste_album and artiste_morceau.lower() == artiste_album.lower():
            artiste_album = artiste_morceau

        # Combiner artiste et featuring en listes pour le morceau et l'album
        artistes_morceau = self._unique_list([artiste_morceau] + title_feats + artist_feats1)
        artistes_album = self._unique_list([artiste_album] + artist_feats2)

        album = self._get_value(audio, 'TALB') if audio else ""
        annee = self._extract_year(self._get_value(audio, 'TDRC')) if audio else ""
        genre = self._get_value(audio, 'TCON') if audio else ""

        cover_data = None
        if audio:
            for tag_key in audio.keys():
                if str(tag_key).startswith('APIC'):
                    cover_data = audio.get(tag_key)
                    break

        data = {
            'titre': titre,
            'artistes_morceau': artistes_morceau,
            'artistes_album': artistes_album,
            'album': album,
            'annee': annee,
            'genre': genre,
            'cover': cover_data,
            'path': path,
            'duration': duration
        }
        return data


    def _get_value(self, audio: ID3, cle: str) -> str:
        if not audio:
            return ""
        frame = audio.get(cle)
        if frame and hasattr(frame, 'text') and len(frame.text) > 0:
            val = frame.text[0]
            if isinstance(val, str):
                return self._normalize_str(val)
            try:
                return self._normalize_str(str(val))
            except Exception:
                return ""
        return ""


    def _normalize_str(self, s: str) -> str:
        if s is None:
            return ""
        return re.sub(r'\s+', ' ', s).strip()


    def _extract_year(self, s: str) -> str:
        if not s:
            return ""
        m = re.search(r'(19|20)\d{2}', s)
        if m:
            return m.group(0)
        m2 = re.search(r'\d{4}', s)
        return m2.group(0) if m2 else ""


    def _split_featuring(self, s: str) -> Tuple[str, List[str]]:
        if not s:
            return "", []
        s = self._normalize_str(s)

        pattern = re.compile(rf'^(?P<main>.*?)[\s\-–—\(\[]*(?:{self._FEAT_KEYWORDS})[:\-\s\.]*(?P<feat>.+?)\)?\s*$', flags=re.I)
        m = pattern.match(s)
        if m:
            main = self._normalize_str(m.group('main'))
            feat_raw = m.group('feat')
            feats = self._split_artists_list(feat_raw)
            return main, feats

        par = re.compile(r'^(?P<main>.*?)\s*\((?P<inside>.*?)\)\s*$')
        m2 = par.match(s)
        if m2:
            inside = m2.group('inside')
            if re.search(self._FEAT_KEYWORDS, inside, flags=re.I):
                main = self._normalize_str(m2.group('main'))
                feat_raw = re.sub(self._FEAT_KEYWORDS, '', inside, flags=re.I).strip(' :.-')
                feats = self._split_artists_list(feat_raw)
                return main, feats

        return s, []


    def _split_artists_list(self, s: str) -> List[str]:
        parts = re.split(r',|&|\band\b|\bx\b|/|;|\+|-', s, flags=re.I)
        return [self._normalize_str(p) for p in parts if self._normalize_str(p)]


    def _unique_list(self, lst: List[str]) -> List[str]:
        seen = set()
        out = []
        for x in lst:
            if not x:
                continue
            low = x.lower()
            if low not in seen:
                seen.add(low)
                out.append(x)
        return out
metadata_reader = MetadataReader()