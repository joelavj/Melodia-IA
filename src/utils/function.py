import os 
from pathlib import Path
import tkinter as tk
from PIL import Image, ImageTk

from utils.logger import get_logger

logger = get_logger(__name__)

# Charger une image PNG et la convertir au format Tkinter
def load_image(image_path: Path, width: int = None, height: int = None) -> tk.PhotoImage:
    """
    Charge une image PNG et la convertit au format Tkinter.
    
    Args:
        image_path: Chemin vers l'image (PNG, JPG, etc.)
        width: Largeur de l'image (optionnel)
        height: Hauteur de l'image (optionnel)
    
    Returns:
        tk.PhotoImage prête à être utilisée dans Tkinter
    """
    try:
        # Ouvre l'image avec PIL
        image = Image.open(image_path)
        
        # Redimensionne si nécessaire
        if width and height:
            image = image.resize((width, height), Image.Resampling.LANCZOS)
        elif width:
            ratio = image.height / image.width
            image = image.resize((width, int(width * ratio)), Image.Resampling.LANCZOS)
        elif height:
            ratio = image.width / image.height
            image = image.resize((int(height * ratio), height), Image.Resampling.LANCZOS)
        
        # Convertit en PhotoImage Tkinter
        return ImageTk.PhotoImage(image)
    except FileNotFoundError:
        logger.warning("Image introuvable à %s", image_path)
        return None
    except Exception as e:
        logger.error("Erreur lors du chargement de l'image %s : %s", image_path, e, exc_info=True)
        return None

# Modifie la permission en tout permis
def modify_permission(path:Path):
    try:
        path.chmod(0o755)
        logger.debug("Permissions modifiées avec succès pour %s", path)
    except FileNotFoundError:
        logger.error("%s est introuvable", path)
        result = None
    except PermissionError:
        logger.error("Droits insuffisants pour modifier %s", path)
        result = None
    except Exception as e:
        logger.error("Erreur non gérée lors de la modification de %s : %s", path, e, exc_info=True)
        result = None
    else:
        result = True
    return result

def get_permission(path:Path)->tuple[bool,bool]:
    read = write = False
    if os.access(path, os.R_OK):
        read = True
    if os.access(path, os.W_OK):
        write = True
    return (read, write)

# Transforme le chemin en absolu
def normalize_path(path:Path)->Path:
    return path.resolve()

# Vérifie si path est à l'intérieur d'other_path
def englobe(path:Path, other_path:Path)->bool:
        return path.is_relative_to(other_path)
