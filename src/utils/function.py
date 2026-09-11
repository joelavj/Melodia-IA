import os 
from pathlib import Path

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
