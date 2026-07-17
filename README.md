# Fichier de conception de Melodia IA

## Vision du projet

    1. Nom du projet:
        Melodia IA

    2. Contexte:
        - Les utilisateurs possèdent souvent des milliers de fichiers audio répartis dans plusieurs dossiers. Les lecteurs de musique classiques permettent la lecture des morceaux mais offrent parfois une gestion limitée de la bibliothèque, des playlists, des métadonnées et de l'organisation des fichiers.
        - Melodia IA est conçu comme un __lecteur de musique de bureau__ capable de:
            - gérer une bibliothèque musicale locale;
            - lire des fichiers audios;
            - organiser les morceaux en playlists et en file d'attente;
            - gérer les métadonnées et les paroles;
            - proposer des fonctionnalités intelligentes liées à l'analyse du genre musical.

    3. But du projet:
        - Fournir un lecteur de musique local moderne permettant à l'utilisateur d'organiser, parcourir et écouter efficacement sa bibliothèque musicale tout en enrichissant automatiquement les informations musicales grâce à des fonctionnalités intelligentes.

    4. Objectifs du projet
        - permettre l'ajout et la gestion de répertoires musicaux.
        - construire automatiquement une bibliothèque à partir des fichiers audio détectés
        - permettre la lecture fluide des morceaux
        - permettre la création et la gestion de playlists
        - permettre la gestion d'une file d'attente de lecture
        - permettre la consultation et la modification des métadonnées et des paroles
        - fournir un mécanisme d'analyse automatique du genre musical basé sur l'IA
        - offrir une interface graphique simple et réactive

    5. Utilisateurs cibles:
        - Le logiciel s'adresse principalement à:
            - des utilisateurs disposant d'une collection musicale locale;
            - des personnes souhaitant gérer leurs fichier audio hors-ligne;
            - des utilsateurs recherchant un lecteur plus organisé qu'un simple lecteur basique;
            - des utilisateurs intéressés par l'enrichissement automatique des informations musicales

    6. Périmètre de la première version (MVP):
        - ajouter et supprimer des répertoires
        - scanner les répertoires
        - construire la bibliothèque musicale
        - afficher les morceaux
        - lire un morceau
        - pause, reprise, arrêt
        - suivant / précédent
        - volume
        - file d'attente simple
        - playlists simples

    7. Contraintes connnues:
        - application de bureau en Python
        - interface graphique avec CustomTKinter
        - lecture audio via Pygame
        - gestion des métadonnées via Mutagen
        - persistance des données via MySQL
        - fonctionnement hors ligne

    8. Critères de reussite
        - un utilisateur pourra ajouter un dossier musical
        - la bibliothèque sera construite automatiquement
        - les morceaux seront consultables et recherchables
        - la lecture audio sera stable
        - les playlists et la file d'attente fonctionneront correctement
        - l'interface restera fluide avec plusieurs milliers de morceaux

## Cahier des charges fonctionnelles

    1. Gestion de la bibliothèque musicale
        - Répertoire:
            - ajouter un répertoire
            - supprimer un répertoire
            - afficher les répertoires enregistrés
            - scanner un répertoire
            - scanner tous les répertoires
            - actualiser la bibliothèque
        - Morceau:
            - afficher tous les morceaux
            - afficher les informations d'un morceau
            - rechercher un morceau
            - trier les morceaux
            - filtrer les morceaux
            - supprimer un morceau de la bibliothèque
            - supprimer un morceau du disque
            - ouvrir l'emplacement du fichier

    2. Lecture audio:
        - lire un morceau
        - mettre en pause
        - reprendre la lecture
        - lire le morceau suivant
        - lire le morceau précédent
        - avancer dans le morceau
        - modifier le volume
        - lire automatiquement le morceau suivant
        - afficher la progression
        - afficher le temps restant
        - afficher la durée

    3. File d'attente:
        - ajouter un morceau
        - ajouter plusieurs morceaux
        - retirer un morceau
        - vider la file
        - changer l'ordre
        - lire immédiatement un morceau
        - sauvegarder la file
        - restaurer la file

    4. Mode de lecture:
        - répeter un morceau
        - répeter toute la file
        - lecture aléatoire
        - lecture normale

    5. Playlist:
        - créer une playlist
        - renommer une playlist
        - supprimer une playlist
        - ajouter un morceau
        - ajouter plusieurs morceaux
        - supprimer un morceau
        - modifier l'ordre
        - lire une playlist

    6. Favoris:
        - ajouter aux favoris
        - retirer des favoris
        - afficher les favoris
        - lire les favoris

    7. Album:
        - afficher tous les albums
        - afficher un album
        - lire un album
        - ajouter un album à la file d'attente

    8. Artiste:
        - afficher tous les artistes
        - afficher un artiste
        - voir les albums d'un artiste
        - voir les morceaux d'un artiste
        - ajouter les morceaux d'un artiste à la file

    9. Métadonnée:
        - afficher les métadonnées
        - modifier les métadonnées
        - modifier la pochette
        - modifier les paroles
        - importer des paroles
        - exporter les paroles
        - modifier la pochette

    10. Recherche:
        - recherche globale
        - recherche par titre
        - recherche par artiste
        - recherche par album
        - recherche par genre
        - recherche par année

    11. Paramètre:
        - choisir les répertoires surveillés
        - choisir le thème
        - modifier le volume par défaut
        - choisir le comportement au démarrage
        - réinitialiser les paramètres

    12. Interface:
        - afficher la bibliothèque
        - afficher la file d'attente
        - afficher la playlist
        - afficher les paroles
        - afficher les informations d'un morceau
        - afficher les notifications

    13. Historique:
        - lire récemment
        - dernier morceaux lus

    14. Statistique:
        - nombre d'écoute
        - date de dernier lecture
        - durée totale écoutée

## Analyse fonctionnelle

    ----- Ajouter un répertoire -----
    1. Objectif:
        Permettre au logiciel d'intégrer un nouveau répertoire à la bibliothèque afin de rendre les morceaux qu'il contient disponibles pour les autres fonctionnalités du système.

    2. Déclencheur:
        - utilistateur clique sur ajouter un nouveau répertoire

    3. Entrées:
        - chemin

    4. Sorties:
        - Si tout se passe bien:
            - le nouveau répertoire est présent dans la bibliothèque
            - les morceaux qui lui appartenaient apparaissent dans la bibliothèque
            - l'utilisateur voit une bibliothèque mis à jour
        - Sinon y a message d'erreur

    5. Scénarios:
        - l'utilisateur clique sur ajouter un nouveau répertoire
        - l'utilisateur entre le chemin du nouveau répertoire
        - le logiciel essaie d'ajouter le chemin
        - le logiciel affiche le résultat en message

    6. Rèle métier:
        - Si le chemin n'existe pas alors
            -> afficher le message: le chemin n'existe pas
        - Si le chemin n'est pas un dossier alors
            -> afficher le message: le chemin ne correspond pas à un dossier
        - Si le chemin existe déjà en tant que répertoire
            -> afficher le message: repertoire déjà existant
        - Si le chemin est contenu dans un autre répertoire alors
            -> afficher le message: le chemin est déjà englobé par un autre répertoire
        - Si le chemin contient les autres répertoires alors
            supprimer les autres répertoires
        - Ajout du nouveau répertoire
        -> afficher le message: le chemin est ajouté avec succès

    7. Conséquence:
        - scanner le nouveau répertoire
        - extraire les métadonnées
        - ajout des nouveaux morceaux
        - actualiser la bibliothèque

---

    ----- Supprimer un répertoire -----
    1. Objectif:
        Permet de retirer un répertoire du bibliothèque

    2. Déclencheur:
        - L'utilisateur clique sur supprimer ce répertoire

    3. Entrées:
        - identifiant du répertoire à supprimer

    4. Sorties:
        Si tout se passe bien:
            - le répertoire n'apparaisse plus dans la bibliothèque
            - les morceaux appartenant au répertoire n'est plus dans la bibliothèque

    5. Scénario:
        - l'utilisateur clique sur supprimer le répertoire
        - le logiciel recupère l'identifiant du répertoire
        - le logiciel supprime le répertoire
        - le logicel supprime les morceaux lié au répertoire
        - le logiciel rafraichi la bibliothèque

    6. Règle metier:
        - supprimer le répertoire par son identifiant
        - supprimer les morceaux appartenant à ce répertoire

    7. Conséquence:
        - mis à jour des playlists, favoris et file d'attente contenant des morceaux appartenant à ce répertoire

---

    ----- Afficher les répertoires enregistré -----
    1. Objectif:
        Permettre à l'utilsateur de savoir les répertoires

    2. Déclencheur:
        - l'utilisateur appuie sur voir tout les répertoires

    3. Entrée:

    4. Sortie:
        Si il y a des répertoires on affiche les répertoires sinon on affiche rien

    5. Scénario:
        - l'utilisateur clique sur voir tout les répertoires
        - le logiciel récupère tout les répertoires
        - le logiciel charge les répertoires
        - le logiciel affiche les répertoires

    6. Règle métier:

    7. Conséquence:

## Modèles métier
