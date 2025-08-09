-- --------------------------------------------------------
-- Hôte:                         127.0.0.1
-- Version du serveur:           8.0.42 - MySQL Community Server - GPL
-- SE du serveur:                Win64
-- HeidiSQL Version:             12.10.0.7000
-- --------------------------------------------------------

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET NAMES utf8 */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

-- Listage de la structure de table mkmpy2. expansions
CREATE TABLE IF NOT EXISTS `expansions` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=0 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Les données exportées n'étaient pas sélectionnées.

-- Listage de la structure de table mkmpy2. logs
CREATE TABLE IF NOT EXISTS `logs` (
  `id` int NOT NULL AUTO_INCREMENT,
  `date_import` datetime NOT NULL,
  `date_import_file` datetime NOT NULL,
  `date_data` date DEFAULT NULL,
  `idStep` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `IDX_F08FC65C3044A0A2` (`idStep`),
  CONSTRAINT `FK_F08FC65C3044A0A2` FOREIGN KEY (`idStep`) REFERENCES `logsteps` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=10 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Les données exportées n'étaient pas sélectionnées.

-- Listage de la structure de table mkmpy2. logsteps
CREATE TABLE IF NOT EXISTS `logsteps` (
  `id` int NOT NULL AUTO_INCREMENT,
  `step` varchar(15) COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=0 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Les données exportées n'étaient pas sélectionnées.

-- Listage de la structure de table mkmpy2. prices
CREATE TABLE IF NOT EXISTS `prices` (
  `id` int NOT NULL AUTO_INCREMENT,
  `date_data` date DEFAULT NULL,
  `avg` decimal(10,2) NOT NULL,
  `low` decimal(10,2) NOT NULL,
  `trend` decimal(10,2) NOT NULL,
  `avg1` decimal(10,2) NOT NULL,
  `avg7` decimal(10,2) NOT NULL,
  `avg30` decimal(10,2) NOT NULL,
  `avg_foil` decimal(10,2) NOT NULL,
  `low_foil` decimal(10,2) NOT NULL,
  `trend_foil` decimal(10,2) NOT NULL,
  `avg1_foil` decimal(10,2) NOT NULL,
  `avg7_foil` decimal(10,2) NOT NULL,
  `avg30_foil` decimal(10,2) NOT NULL,
  `idProduct` int DEFAULT NULL,
  `idLog` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `IDX_E4CB6D59C3F36F5F` (`idProduct`),
  KEY `IDX_E4CB6D59AE777542` (`idLog`),
  CONSTRAINT `FK_E4CB6D59AE777542` FOREIGN KEY (`idLog`) REFERENCES `logs` (`id`),
  CONSTRAINT `FK_E4CB6D59C3F36F5F` FOREIGN KEY (`idProduct`) REFERENCES `products` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=0 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Les données exportées n'étaient pas sélectionnées.

-- Listage de la structure de table mkmpy2. products
CREATE TABLE IF NOT EXISTS `products` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `id_meta_card` int NOT NULL,
  `date_added` datetime NOT NULL,
  `idExpansion` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `IDX_B3BA5A5AC837024` (`idExpansion`),
  CONSTRAINT `FK_B3BA5A5AC837024` FOREIGN KEY (`idExpansion`) REFERENCES `expansions` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=0 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Les données exportées n'étaient pas sélectionnées.

-- Listage de la structure de table mkmpy2. scryfall_products
CREATE TABLE IF NOT EXISTS `scryfall_products` (
  `id` varchar(36) COLLATE utf8mb4_unicode_ci NOT NULL,
  `card_market_id_id` int DEFAULT NULL,
  `oracle_id` varchar(36) COLLATE utf8mb4_unicode_ci NOT NULL,
  `scryfall_uri` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `img_normal_uri` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `img_large_uri` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `img_png_uri` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `img_artcrop_uri` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `img_bordercrop_uri` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `reserved` tinyint(1) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `IDX_F32CB476A4578F27` (`card_market_id_id`),
  CONSTRAINT `FK_F32CB476A4578F27` FOREIGN KEY (`card_market_id_id`) REFERENCES `products` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Les données exportées n'étaient pas sélectionnées.

-- Listage des données de la table mkmpy2.logsteps : ~3 rows (environ)
INSERT INTO `logsteps` (`id`, `step`) VALUES
	(10, 'ongoing'),
	(50, 'finished'),
	(90, 'too early');

INSERT INTO `logs` (`id`, `date_import`, `date_import_file`, `date_data`, `idStep`) VALUES
	(1, '2025-01-01 00:00:00', '2024-12-31 22:00:00', '2025-01-01', 50);

/*!40103 SET TIME_ZONE=IFNULL(@OLD_TIME_ZONE, 'system') */;
/*!40101 SET SQL_MODE=IFNULL(@OLD_SQL_MODE, '') */;
/*!40014 SET FOREIGN_KEY_CHECKS=IFNULL(@OLD_FOREIGN_KEY_CHECKS, 1) */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40111 SET SQL_NOTES=IFNULL(@OLD_SQL_NOTES, 1) */;
