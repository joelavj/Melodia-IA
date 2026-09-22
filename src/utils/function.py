import os 
from pathlib import Path
import tkinter as tk
from PIL import Image, ImageTk

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
        print(f"Erreur : Image introuvable à {image_path}")
        return None
    except Exception as e:
        print(f"Erreur lors du chargement de l'image : {e}")
        return None

# Modifie la permission en tout permis
def modify_permission(path:Path):
    try:
        path.chmod(0o755)
        print("Permissions modifiées avec succès")
    except FileNotFoundError:
        result = print(f"Erreur : {path} est introuvable")
    except PermissionError:
        result = print(f"Erreur : Droits insuffisants pour modifier {path}")
    except:
        result = "Erreur : Cette erreur n'est pas gérer"
    else:
        result = True
    finally:
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
