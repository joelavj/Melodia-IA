from mutagen.id3 import ID3
from pathlib import Path
from typing import Tuple, List
import re

FEAT_KEYWORDS = r'(?:feat(?:uring)?|ft|featuring|with)\.?'

def extract(path: Path) -> dict:
    """Extrait des métadonnées d'un fichier MP3 en gérant plusieurs cas corner.

    Retourne un dict avec les clés : titre, artiste_morceau, artiste_album,
    album, annee, genre, featuring (liste).
    """
    audio = ID3(str(path))

    titre_raw = get_value(audio, 'TIT2')
    titre, title_feats = split_featuring(titre_raw)

    artiste_morceau_raw = get_value(audio, 'TPE1')
    artiste_album_raw = get_value(audio, 'TPE2')

    # Nettoyage et extraction des featuring depuis les champs artiste
    artiste_morceau, artist_feats1 = split_featuring(artiste_morceau_raw)
    artiste_album, artist_feats2 = split_featuring(artiste_album_raw)

    # Si artiste morceau manquant, utiliser artiste album
    if not artiste_morceau and artiste_album:
        artiste_morceau = artiste_album

    # Si les deux présents mais seulement différence de casse, harmoniser
    if artiste_morceau and artiste_album and artiste_morceau.lower() == artiste_album.lower():
        artiste_album = artiste_morceau

    # Combiner artiste et featuring en listes pour le morceau et l'album
    artistes_morceau = unique_list([artiste_morceau] + title_feats + artist_feats1)
    artistes_album = unique_list([artiste_album] + artist_feats2)

    album = get_value(audio, 'TALB')
    annee = extract_year(get_value(audio, 'TDRC'))
    genre = get_value(audio, 'TCON')

    data = {
        'titre': titre,
        'artistes_morceau': artistes_morceau,
        'artistes_album': artistes_album,
        'album': album,
        'annee': annee,
        'genre': genre,
    }
    return data


def get_value(audio: ID3, cle: str) -> str:
    frame = audio.get(cle)
    if frame and hasattr(frame, 'text') and len(frame.text) > 0:
        val = frame.text[0]
        if isinstance(val, str):
            return normalize_str(val)
        try:
            return normalize_str(str(val))
        except Exception:
            return ""
    return ""


def normalize_str(s: str) -> str:
    if s is None:
        return ""
    # collapse whitespace and trim
    return re.sub(r'\s+', ' ', s).strip()


def extract_year(s: str) -> str:
    if not s:
        return ""
    # rechercher 4 chiffres représentant l'année
    m = re.search(r'(19|20)\d{2}', s)
    if m:
        return m.group(0)
    # fallback: digits
    m2 = re.search(r'\d{4}', s)
    return m2.group(0) if m2 else ""


def split_featuring(s: str) -> Tuple[str, List[str]]:
    """Sépare la partie principale et retourne une liste de featuring trouvés.

    Exemples gérés :
    - "Artist feat. Someone & Someone"
    - "Artist (feat. Someone)"
    - "Artist ft Someone"
    - "Song Title (with Guest)"
    """
    if not s:
        return "", []
    s = normalize_str(s)

    # pattern principal : capture avant et après un marqueur feat
    pattern = re.compile(rf'^(?P<main>.*?)[\s\-–—\(\[]*(?:{FEAT_KEYWORDS})[:\-\s\.]*(?P<feat>.+?)\)?\s*$', flags=re.I)
    m = pattern.match(s)
    if m:
        main = normalize_str(m.group('main'))
        feat_raw = m.group('feat')
        feats = split_artists_list(feat_raw)
        return main, feats

    # cas où le featuring est dans des parenthèses mais sans mot-clé au début
    par = re.compile(r'^(?P<main>.*?)\s*\((?P<inside>.*?)\)\s*$')
    m2 = par.match(s)
    if m2:
        inside = m2.group('inside')
        if re.search(FEAT_KEYWORDS, inside, flags=re.I):
            main = normalize_str(m2.group('main'))
            # retirer le mot-clé
            feat_raw = re.sub(FEAT_KEYWORDS, '', inside, flags=re.I).strip(' :.-')
            feats = split_artists_list(feat_raw)
            return main, feats

    # aucun featuring détecté
    return s, []


def split_artists_list(s: str) -> List[str]:
    # séparer par délimiteurs courants
    parts = re.split(r',|&|\band\b|\bx\b|/|;|\+|-', s, flags=re.I)
    return [normalize_str(p) for p in parts if normalize_str(p)]


def unique_list(lst: List[str]) -> List[str]:
    seen = set()
    out = []
    for x in lst:
        low = x.lower()
        if low not in seen and x:
            seen.add(low)
            out.append(x)
    return out

