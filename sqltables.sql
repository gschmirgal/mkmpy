--
-- Base de données : `mkmpy`
--

-- --------------------------------------------------------

--
-- Structure de la table `expansions`
--

CREATE TABLE `expansions` (
  `id` int(11) NOT NULL,
  `name` varchar(255) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Structure de la table `log`
--

CREATE TABLE `log` (
  `id` int(11) NOT NULL,
  `dateImport` datetime NOT NULL DEFAULT current_timestamp(),
  `dateImportFile` timestamp NOT NULL DEFAULT current_timestamp(),
  `status` varchar(255) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Structure de la table `prices`
--

CREATE TABLE `prices` (
  `id` int(11) NOT NULL,
  `idProduct` int(11) DEFAULT NULL,
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
  `avg30Foil` decimal(10,2) NOT NULL,
  `dateExport` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Structure de la table `products`
--

CREATE TABLE `products` (
  `id` int(11) NOT NULL,
  `name` varchar(255) NOT NULL,
  `idExpansion` int(11) NOT NULL,
  `idMetacard` int(11) NOT NULL,
  `dateAdded` datetime NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--init table logs

INSERT INTO `logs` (`id`, `dateImport`, `dateImportFile`, `status`) VALUES
(1, '2025-01-01 00:00:00', '2024-12-31 23:00:00', 'OK');


--
-- Index pour les tables déchargées
--

--
-- Index pour la table `expansions`
--
ALTER TABLE `expansions`
  ADD PRIMARY KEY (`id`);

--
-- Index pour la table `log`
--
ALTER TABLE `log`
  ADD PRIMARY KEY (`id`);

--
-- Index pour la table `prices`
--
ALTER TABLE `prices`
  ADD PRIMARY KEY (`id`),
  ADD KEY `idProduct` (`idProduct`);

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
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT pour la table `log`
--
ALTER TABLE `log`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT pour la table `prices`
--
ALTER TABLE `prices`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT pour la table `products`
--
ALTER TABLE `products`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- Contraintes pour les tables déchargées
--

--
-- Contraintes pour la table `prices`
--
ALTER TABLE `prices`
  ADD CONSTRAINT `prices_ibfk_1` FOREIGN KEY (`idProduct`) REFERENCES `products` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION;

--
-- Contraintes pour la table `products`
--
ALTER TABLE `products`
  ADD CONSTRAINT `products_ibfk_1` FOREIGN KEY (`idExpansion`) REFERENCES `expansions` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION;
COMMIT;
