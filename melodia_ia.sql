-- --------------------------------------------------------
-- Hôte:                         127.0.0.1
-- Version du serveur:           8.4.3 - MySQL Community Server - GPL
-- SE du serveur:                Win64
-- HeidiSQL Version:             12.8.0.6908
-- --------------------------------------------------------

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET NAMES utf8 */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;


-- Listage de la structure de la base pour melodia_ia
CREATE DATABASE IF NOT EXISTS `melodia_ia` /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci */ /*!80016 DEFAULT ENCRYPTION='N' */;
USE `melodia_ia`;

-- Listage de la structure de table melodia_ia. album
CREATE TABLE IF NOT EXISTS `album` (
  `id_album` int NOT NULL AUTO_INCREMENT,
  `titre` varchar(255) NOT NULL,
  `annee_sortie` year DEFAULT NULL,
  PRIMARY KEY (`id_album`)
) ENGINE=InnoDB AUTO_INCREMENT=45 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Les données exportées n'étaient pas sélectionnées.

-- Listage de la structure de table melodia_ia. artiste
CREATE TABLE IF NOT EXISTS `artiste` (
  `id_artiste` int NOT NULL AUTO_INCREMENT,
  `nom` varchar(255) NOT NULL,
  PRIMARY KEY (`id_artiste`),
  UNIQUE KEY `nom_scene` (`nom`) USING BTREE
) ENGINE=InnoDB AUTO_INCREMENT=44 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Les données exportées n'étaient pas sélectionnées.

-- Listage de la structure de table melodia_ia. artiste_album
CREATE TABLE IF NOT EXISTS `artiste_album` (
  `id_artiste` int NOT NULL,
  `id_album` int NOT NULL,
  PRIMARY KEY (`id_artiste`,`id_album`),
  KEY `FK__album` (`id_album`),
  CONSTRAINT `FK__album` FOREIGN KEY (`id_album`) REFERENCES `album` (`id_album`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `FK__artiste` FOREIGN KEY (`id_artiste`) REFERENCES `artiste` (`id_artiste`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Les données exportées n'étaient pas sélectionnées.

-- Listage de la structure de table melodia_ia. artiste_morceau
CREATE TABLE IF NOT EXISTS `artiste_morceau` (
  `id_artiste` int NOT NULL,
  `id_morceau` int NOT NULL,
  PRIMARY KEY (`id_artiste`,`id_morceau`),
  KEY `FK__morceau` (`id_morceau`),
  CONSTRAINT `FK__artiste2` FOREIGN KEY (`id_artiste`) REFERENCES `artiste` (`id_artiste`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `FK__morceau` FOREIGN KEY (`id_morceau`) REFERENCES `morceau` (`id_morceau`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Les données exportées n'étaient pas sélectionnées.

-- Listage de la structure de table melodia_ia. morceau
CREATE TABLE IF NOT EXISTS `morceau` (
  `id_morceau` int NOT NULL AUTO_INCREMENT,
  `titre` varchar(255) NOT NULL,
  `chemin` varchar(255) NOT NULL,
  `genre` varchar(255) NOT NULL,
  `id_repertoire` int NOT NULL DEFAULT (0),
  `id_album` int NOT NULL DEFAULT (0),
  PRIMARY KEY (`id_morceau`),
  UNIQUE KEY `chemin` (`chemin`),
  KEY `FK__album2` (`id_album`),
  KEY `FK__repertoire` (`id_repertoire`),
  CONSTRAINT `FK__album2` FOREIGN KEY (`id_album`) REFERENCES `album` (`id_album`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `FK__repertoire` FOREIGN KEY (`id_repertoire`) REFERENCES `repertoire` (`id_repertoire`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=92 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Les données exportées n'étaient pas sélectionnées.

-- Listage de la structure de table melodia_ia. playlist
CREATE TABLE IF NOT EXISTS `playlist` (
  `id_playlist` int NOT NULL AUTO_INCREMENT,
  `nom` varchar(50) NOT NULL,
  PRIMARY KEY (`id_playlist`),
  UNIQUE KEY `nom` (`nom`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Les données exportées n'étaient pas sélectionnées.

-- Listage de la structure de table melodia_ia. playlist_morceau
CREATE TABLE IF NOT EXISTS `playlist_morceau` (
  `id_morceau` int NOT NULL,
  `id_playlist` int NOT NULL,
  `num_ordre` int NOT NULL,
  PRIMARY KEY (`id_morceau`,`id_playlist`),
  KEY `FK_playlist_morceau_playlist` (`id_playlist`),
  CONSTRAINT `FK_playlist_morceau_morceau` FOREIGN KEY (`id_morceau`) REFERENCES `morceau` (`id_morceau`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `FK_playlist_morceau_playlist` FOREIGN KEY (`id_playlist`) REFERENCES `playlist` (`id_playlist`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Les données exportées n'étaient pas sélectionnées.

-- Listage de la structure de table melodia_ia. repertoire
CREATE TABLE IF NOT EXISTS `repertoire` (
  `id_repertoire` int NOT NULL AUTO_INCREMENT,
  `chemin` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL DEFAULT '0',
  PRIMARY KEY (`id_repertoire`),
  UNIQUE KEY `chemin` (`chemin`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Les données exportées n'étaient pas sélectionnées.

/*!40103 SET TIME_ZONE=IFNULL(@OLD_TIME_ZONE, 'system') */;
/*!40101 SET SQL_MODE=IFNULL(@OLD_SQL_MODE, '') */;
/*!40014 SET FOREIGN_KEY_CHECKS=IFNULL(@OLD_FOREIGN_KEY_CHECKS, 1) */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40111 SET SQL_NOTES=IFNULL(@OLD_SQL_NOTES, 1) */;
