--
-- Base de données : `mkmpy`
--

-- --------------------------------------------------------

--
-- Structure de la table `expansions`
--

CREATE TABLE `expansions` (
  `id` int NOT NULL,
  `name` varchar(255) COLLATE utf8mb4_general_ci NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Structure de la table `logs`
--

CREATE TABLE `logs` (
  `id` int NOT NULL,
  `dateImport` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `dateImportFile` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `dateData` date DEFAULT NULL,
  `idStep` int NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Déchargement des données de la table `logs`
--

INSERT INTO `logs` (`id`, `dateImport`, `dateImportFile`, `dateData`, `idStep`) VALUES
(1, '2025-01-01 00:00:00', '2024-12-31 22:00:00', '2025-01-01', 50);

-- --------------------------------------------------------

--
-- Structure de la table `logsteps`
--

CREATE TABLE `logsteps` (
  `id` int NOT NULL,
  `step` varchar(15) COLLATE utf8mb4_general_ci DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Déchargement des données de la table `logsteps`
--

INSERT INTO `logsteps` (`id`, `step`) VALUES
(10, 'ongoing'),
(50, 'OK'),
(90, 'too early');

-- --------------------------------------------------------

--
-- Structure de la table `prices`
--

CREATE TABLE `prices` (
  `id` int NOT NULL,
  `idProduct` int DEFAULT NULL,
  `idLog` int NOT NULL,
  `dateData` date DEFAULT NULL,
  `avg` decimal(10,2) NOT NULL,
  `low` decimal(10,2) NOT NULL,
  `trend` decimal(10,2) NOT NULL,
  `avg1` decimal(10,2) NOT NULL,
  `avg7` decimal(10,2) NOT NULL,
  `avg30` decimal(10,2) NOT NULL,
  `avfFoil` decimal(10,2) NOT NULL,
  `lowFoil` decimal(10,2) NOT NULL,
  `trendFoil` decimal(10,2) NOT NULL,
  `avg1Foil` decimal(10,2) NOT NULL,
  `avg7Foil` decimal(10,2) NOT NULL,
  `avg30Foil` decimal(10,2) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Structure de la table `products`
--

CREATE TABLE `products` (
  `id` int NOT NULL,
  `name` varchar(255) COLLATE utf8mb4_general_ci NOT NULL,
  `idExpansion` int NOT NULL,
  `idMetacard` int NOT NULL,
  `dateAdded` datetime NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Index pour les tables déchargées
--

--
-- Index pour la table `expansions`
--
ALTER TABLE `expansions`
  ADD PRIMARY KEY (`id`);

--
-- Index pour la table `logs`
--
ALTER TABLE `logs`
  ADD PRIMARY KEY (`id`),
  ADD KEY `idstatus` (`idStep`);

--
-- Index pour la table `logsteps`
--
ALTER TABLE `logsteps`
  ADD PRIMARY KEY (`id`);

--
-- Index pour la table `prices`
--
ALTER TABLE `prices`
  ADD PRIMARY KEY (`id`),
  ADD KEY `idProduct` (`idProduct`),
  ADD KEY `prices_ibfk_2` (`idLog`);

--
-- Index pour la table `products`
--
ALTER TABLE `products`
  ADD PRIMARY KEY (`id`),
  ADD KEY `idExpansion` (`idExpansion`),
  ADD KEY `idMetacard` (`idMetacard`);

--
-- AUTO_INCREMENT pour les tables déchargées
--

--
-- AUTO_INCREMENT pour la table `expansions`
--
ALTER TABLE `expansions`
  MODIFY `id` int NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT pour la table `logs`
--
ALTER TABLE `logs`
  MODIFY `id` int NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=12;

--
-- AUTO_INCREMENT pour la table `prices`
--
ALTER TABLE `prices`
  MODIFY `id` int NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT pour la table `products`
--
ALTER TABLE `products`
  MODIFY `id` int NOT NULL AUTO_INCREMENT;

--
-- Contraintes pour les tables déchargées
--

--
-- Contraintes pour la table `logs`
--
ALTER TABLE `logs`
  ADD CONSTRAINT `logs_ibfk_1` FOREIGN KEY (`idStep`) REFERENCES `logsteps` (`id`);

--
-- Contraintes pour la table `prices`
--
ALTER TABLE `prices`
  ADD CONSTRAINT `prices_ibfk_1` FOREIGN KEY (`idProduct`) REFERENCES `products` (`id`),
  ADD CONSTRAINT `prices_ibfk_2` FOREIGN KEY (`idLog`) REFERENCES `logs` (`id`);

--
-- Contraintes pour la table `products`
--
ALTER TABLE `products`
  ADD CONSTRAINT `products_ibfk_1` FOREIGN KEY (`idExpansion`) REFERENCES `expansions` (`id`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
