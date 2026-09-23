try:
    # Optionnel : si python-dotenv est installé, charge les variables du
    # fichier .env (identifiants MySQL, niveau de log) avant de démarrer.
    # Sans cette dépendance, les variables peuvent être définies autrement
    # (variables d'environnement système, script de lancement, etc.).
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from views.app import App

window = App()
window.mainloop()
