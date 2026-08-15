# Mélod'IA

Mélod'IA est une application de gestion de musique qui permet aux utilisateurs de naviguer, d'écouter et de gérer leurs chansons et playlists. Ce projet utilise le framework CustomTkinter pour créer une interface utilisateur moderne et réactive.

## Structure du projet

Le projet est organisé selon le modèle MVC (Modèle-Vue-Contrôleur) et se compose des répertoires suivants :

- **src/** : Contient le code source de l'application.
  - **controllers/** : Gère la logique de l'application et les interactions utilisateur.
  - **views/** : Contient les composants de l'interface utilisateur.
  - **models/** : Définit les structures de données et les modèles de l'application.
  - **services/** : Fournit des fonctionnalités spécifiques, comme la gestion audio et l'importation de chansons.
  - **repositories/** : Interagit avec la base de données ou le stockage des chansons.
  - **utils/** : Contient des fonctions utilitaires pour des tâches courantes.

- **docs/** : Documentation des problèmes connus et des améliorations à apporter à la partie backend.   
- **tests/** : Contient les tests unitaires pour les modèles, services et contrôleurs.
- **requirements.txt** : Liste des dépendances nécessaires pour exécuter le projet.
- **pyproject.toml** : Configuration du projet Python.
- **.gitignore** : Fichiers et dossiers à ignorer par Git.

## Problèmes à résoudre dans la partie backend

1. **Gestion des erreurs** : Assurez-vous que chaque service et contrôleur gère correctement les exceptions et les erreurs, en fournissant des messages d'erreur clairs à l'utilisateur.
2. **Tests unitaires** : Vérifiez que tous les composants (modèles, services, contrôleurs) sont couverts par des tests unitaires pour garantir leur bon fonctionnement.
3. **Séparation des préoccupations** : Assurez-vous que chaque classe et module a une responsabilité unique pour respecter le principe de séparation des préoccupations.
4. **Performance** : Évaluez les performances des services, en particulier ceux qui interagissent avec des fichiers ou des bases de données, et optimisez-les si nécessaire.

## Installation

Pour installer les dépendances du projet, exécutez la commande suivante :

```
pip install -r requirements.txt
```

## Utilisation

Pour démarrer l'application, exécutez le fichier `main.py` :

```
python src/main.py
```

## Contribuer

Les contributions sont les bienvenues ! Veuillez soumettre une demande de tirage pour toute amélioration ou correction de bogue.