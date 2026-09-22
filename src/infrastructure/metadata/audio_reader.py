"""Lecteur de métadonnées audio générique.

Contrairement à l'ancien ``mp3_reader``, ce module ne se limite plus au
format MP3/ID3 : il s'appuie sur la détection automatique de Mutagen
(``mutagen.File``) puis choisit la bonne stratégie de lecture de tags selon
le conteneur détecté (ID3 pour MP3/WAV, VorbisComment pour FLAC/OGG,
atomes iTunes pour MP4/M4A, ASF pour WMA...).

Formats pris en charge nativement : MP3, FLAC, OGG (Vorbis/Opus), WAV,
M4A/MP4 (AAC/ALAC), WMA, ainsi que tout autre conteneur reconnu par
Mutagen dont on pourra au moins extraire la durée.
"""

from pathlib import Path
from typing import List, Optional, Tuple
import base64
import re

from mutagen import File as mutagen_file
from mutagen.id3 import ID3
from mutagen.flac import FLAC, Picture
from mutagen.oggvorbis import OggVorbis
from mutagen.oggopus import OggOpus
from mutagen.mp4 import MP4, MP4Cover
from mutagen.asf import ASF
from mutagen.wave import WAVE

# Extensions de fichiers audio pris en charge par l'application.
SUPPORTED_EXTENSIONS = {
    ".mp3", ".flac", ".ogg", ".oga", ".opus",
    ".wav", ".wave", ".m4a", ".mp4", ".aac", ".wma",
}


class CoverData:
    """Représentation normalisée d'une pochette, quel que soit le format
    audio d'origine. Expose la même interface (``mime``/``data``) que la
    frame ``APIC`` de Mutagen afin de rester compatible avec
    ``cover_storage`` sans le modifier.
    """

    def __init__(self, data: bytes, mime: str) -> None:
        self.data = data
        self.mime = mime


class UnsupportedAudioFormatError(Exception):
    """Le fichier n'a pas pu être lu ou décodé par Mutagen."""


class MetadataReader:

    _FEAT_KEYWORDS = r'(?:feat(?:uring)?|ft|featuring|with)\.?'

    def extract(self, path: Path) -> dict:
        """Extrait les métadonnées d'un fichier audio, quel que soit son
        format, en gérant plusieurs cas particuliers.

        Retourne un dict avec les clés : titre, artiste_morceau,
        artiste_album, album, annee, genre, featuring (liste), cover,
        path, duration.
        """
        path = Path(path)
        audio = mutagen_file(str(path))
        if audio is None:
            raise UnsupportedAudioFormatError(
                f"Format audio non supporté ou fichier corrompu : {path}"
            )

        duration = float(getattr(audio.info, "length", 0) or 0)

        titre_raw, artiste_morceau_raw, artiste_album_raw, album, annee, genre, cover_data = (
            self._read_tags(audio)
        )

        # Repli sur le nom du fichier si aucun titre n'est présent dans les tags
        if not titre_raw:
            titre_raw = path.stem

        titre, title_feats = self._split_featuring(titre_raw)

        # Nettoyage et extraction des featuring depuis les champs artiste
        artiste_morceau, artist_feats1 = self._split_featuring(artiste_morceau_raw)
        artiste_album, artist_feats2 = self._split_featuring(artiste_album_raw)

        # Si artiste morceau manquant, utiliser artiste album
        if not artiste_morceau and artiste_album:
            artiste_morceau = artiste_album

        # Si artiste toujours manquant, indiquer un artiste par défaut
        if not artiste_morceau:
            artiste_morceau = "Artiste inconnu"

        # Si les deux présents mais seulement différence de casse, harmoniser
        if artiste_morceau and artiste_album and artiste_morceau.lower() == artiste_album.lower():
            artiste_album = artiste_morceau

        # Combiner artiste et featuring en listes pour le morceau et l'album
        artistes_morceau = self._unique_list([artiste_morceau] + title_feats + artist_feats1)
        artistes_album = self._unique_list([artiste_album or artiste_morceau] + artist_feats2)

        if not album:
            album = "Album inconnu"

        data = {
            'titre': titre,
            'artistes_morceau': artistes_morceau,
            'artistes_album': artistes_album,
            'album': album,
            'annee': annee,
            'genre': genre,
            'cover': cover_data,
            'path': path,
            'duration': duration,
        }
        return data

    # ------------------------------------------------------------------
    # Lecture des tags selon le conteneur détecté
    # ------------------------------------------------------------------

    def _read_tags(self, audio) -> Tuple[str, str, str, str, str, str, Optional[CoverData]]:
        if isinstance(audio, WAVE):
            return self._read_id3(audio.tags)
        if isinstance(audio, FLAC):
            return self._read_vorbis_comment(audio.tags, self._flac_cover(audio))
        if isinstance(audio, (OggVorbis, OggOpus)):
            return self._read_vorbis_comment(audio.tags, self._ogg_cover(audio.tags))
        if isinstance(audio, MP4):
            return self._read_mp4(audio.tags)
        if isinstance(audio, ASF):
            return self._read_asf(audio.tags)
        if isinstance(audio.tags, ID3) or hasattr(audio.tags, "getall"):
            # MP3 et tout autre conteneur portant des tags ID3 (ID3 générique)
            return self._read_id3(audio.tags)
        # Format inconnu ou sans tags exploitables : on retombe sur les valeurs vides,
        # seule la durée (déjà lue) et le nom de fichier (utilisé plus haut) subsistent.
        return "", "", "", "", "", "", None

    def _read_id3(self, tags) -> Tuple[str, str, str, str, str, str, Optional[CoverData]]:
        if tags is None:
            return "", "", "", "", "", "", None
        titre = self._get_id3_value(tags, 'TIT2')
        artiste_morceau = self._get_id3_value(tags, 'TPE1')
        artiste_album = self._get_id3_value(tags, 'TPE2')
        album = self._get_id3_value(tags, 'TALB')
        annee = self._extract_year(self._get_id3_value(tags, 'TDRC'))
        genre = self._normalize_genre(self._get_id3_value(tags, 'TCON'))

        cover_data = None
        for tag_key in tags.keys():
            if str(tag_key).startswith('APIC'):
                frame = tags.get(tag_key)
                if frame is not None:
                    cover_data = CoverData(frame.data, frame.mime)
                break
        return titre, artiste_morceau, artiste_album, album, annee, genre, cover_data

    def _get_id3_value(self, tags, cle: str) -> str:
        frame = tags.get(cle)
        if frame and hasattr(frame, 'text') and len(frame.text) > 0:
            val = frame.text[0]
            if isinstance(val, str):
                return self._normalize_str(val)
            try:
                return self._normalize_str(str(val))
            except Exception:
                return ""
        return ""

    def _read_vorbis_comment(self, tags, cover_data: Optional[CoverData]) -> Tuple[str, str, str, str, str, str, Optional[CoverData]]:
        if tags is None:
            return "", "", "", "", "", "", cover_data
        titre = self._get_vorbis_value(tags, 'title')
        artiste_morceau = self._get_vorbis_value(tags, 'artist')
        artiste_album = self._get_vorbis_value(tags, 'albumartist')
        album = self._get_vorbis_value(tags, 'album')
        annee = self._extract_year(
            self._get_vorbis_value(tags, 'date') or self._get_vorbis_value(tags, 'year')
        )
        genre = self._normalize_genre(self._get_vorbis_value(tags, 'genre'))
        return titre, artiste_morceau, artiste_album, album, annee, genre, cover_data

    def _get_vorbis_value(self, tags, cle: str) -> str:
        values = tags.get(cle)
        if values:
            return self._normalize_str(str(values[0]))
        return ""

    def _flac_cover(self, audio: FLAC) -> Optional[CoverData]:
        if audio.pictures:
            pic = audio.pictures[0]
            return CoverData(pic.data, pic.mime)
        return None

    def _ogg_cover(self, tags) -> Optional[CoverData]:
        # Les pochettes OGG/Opus sont encodées en base64 au format
        # "METADATA_BLOCK_PICTURE" (spécification FLAC réutilisée).
        raw = tags.get('metadata_block_picture')
        if not raw:
            return None
        try:
            picture_data = base64.b64decode(raw[0])
            pic = Picture(picture_data)
            return CoverData(pic.data, pic.mime)
        except Exception:
            return None

    def _read_mp4(self, tags) -> Tuple[str, str, str, str, str, str, Optional[CoverData]]:
        if tags is None:
            return "", "", "", "", "", "", None
        titre = self._get_mp4_value(tags, '\xa9nam')
        artiste_morceau = self._get_mp4_value(tags, '\xa9ART')
        artiste_album = self._get_mp4_value(tags, 'aART')
        album = self._get_mp4_value(tags, '\xa9alb')
        annee = self._extract_year(self._get_mp4_value(tags, '\xa9day'))
        genre = self._normalize_genre(self._get_mp4_value(tags, '\xa9gen'))

        cover_data = None
        covers = tags.get('covr')
        if covers:
            cover = covers[0]
            mime = 'image/png' if getattr(cover, 'imageformat', None) == MP4Cover.FORMAT_PNG else 'image/jpeg'
            cover_data = CoverData(bytes(cover), mime)
        return titre, artiste_morceau, artiste_album, album, annee, genre, cover_data

    def _get_mp4_value(self, tags, cle: str) -> str:
        values = tags.get(cle)
        if values:
            return self._normalize_str(str(values[0]))
        return ""

    def _read_asf(self, tags) -> Tuple[str, str, str, str, str, str, Optional[CoverData]]:
        if tags is None:
            return "", "", "", "", "", "", None
        titre = self._get_asf_value(tags, 'Title')
        artiste_morceau = self._get_asf_value(tags, 'Author')
        artiste_album = self._get_asf_value(tags, 'WM/AlbumArtist')
        album = self._get_asf_value(tags, 'WM/AlbumTitle')
        annee = self._extract_year(self._get_asf_value(tags, 'WM/Year'))
        genre = self._normalize_genre(self._get_asf_value(tags, 'WM/Genre'))

        cover_data = None
        picture_attrs = tags.get('WM/Picture')
        if picture_attrs:
            try:
                from mutagen.asf import ASFByteArrayAttribute
                raw = picture_attrs[0].value if isinstance(picture_attrs[0], ASFByteArrayAttribute) else bytes(picture_attrs[0])
                pic = Picture(raw)
                cover_data = CoverData(pic.data, pic.mime)
            except Exception:
                cover_data = None
        return titre, artiste_morceau, artiste_album, album, annee, genre, cover_data

    def _get_asf_value(self, tags, cle: str) -> str:
        values = tags.get(cle)
        if values:
            return self._normalize_str(str(values[0]))
        return ""

    # ------------------------------------------------------------------
    # Normalisation partagée (commune à tous les formats)
    # ------------------------------------------------------------------

    def _normalize_str(self, s: str) -> str:
        if s is None:
            return ""
        return re.sub(r'\s+', ' ', s).strip()

    def _normalize_genre(self, genre: str) -> str:
        """Nettoie une valeur de genre brute.

        Certains fichiers MP3 anciens stockent le genre au format ID3v1
        sous forme d'index numérique entre parenthèses, ex ``(17)`` pour
        "Rock". Mutagen le résout généralement tout seul, mais on
        neutralise ici les résidus numériques bruts pour ne pas polluer
        la base avec un genre illisible.
        """
        genre = self._normalize_str(genre)
        if not genre:
            return ""
        if re.fullmatch(r'\(?\d+\)?', genre):
            return ""
        return genre

    def _extract_year(self, s: str) -> str:
        if not s:
            return ""
        m = re.search(r'(19|20)\d{2}', s)
        if m:
            return m.group(0)
        m2 = re.search(r'\d{4}', s)
        return m2.group(0) if m2 else ""

    def _split_featuring(self, s: str) -> Tuple[str, List[str]]:
        """Sépare la partie principale et retourne une liste de featuring trouvés.

        Exemples gérés :
        - "Artist feat. Someone & Someone"
        - "Artist (feat. Someone)"
        - "Artist ft Someone"
        - "Song Title (with Guest)"
        """
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
