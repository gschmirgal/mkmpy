"""
MKMPy - Cardmarket Data Importer

Ce projet automatise la récupération, la transformation et l'importation des données produits, prix et extensions Magic: The Gathering depuis Cardmarket et Scryfall vers une base MySQL.

Fonctionnalités principales :
- Récupération de données via API et web scraping (contournement Cloudflare)
- Génération de fichiers CSV intermédiaires
- Import rapide en base MySQL (désactivable : [Database] enabled = false)
- Matching des cartes Scryfall / Cardmarket
- Système de log et contrôle d'exécution

Structure :
- mkmpy/cardmarket.py : collecte Cardmarket et génération CSV
- mkmpy/scryfall.py : collecte Scryfall et génération CSV
- mkmpy/datasets.py : tables cibles et correspondance des colonnes
- mkmpy/csvwriter.py : écriture des CSV au format LOAD DATA
- mkmpy/db.py : gestion MySQL
- mkmpy/import_log.py : suivi des imports (table logs)
- mkmpy/matcher.py : matching Scryfall / Cardmarket
- mkmpy/lib.py : configuration et utilitaires
- launch.py : script principal

Prérequis : voir README.md
"""

import logging
import sys

from mkmpy.cardmarket import CardmarketSource
from mkmpy.datasets import EXPANSIONS, PRICES, PRODUCTS, SCRYFALL_DATASETS
from mkmpy.db import MySQLConnectionManager
from mkmpy.import_log import ImportLog
from mkmpy.lib import create_session, get_boolean, get_csv_dir, load_config, setup_logging
from mkmpy.matcher import Matcher
from mkmpy.scryfall import ScryfallSource

logger = logging.getLogger("mkmpy")

# Nom provisoire des extensions créées automatiquement, à renommer à la main
# (ou renommées automatiquement au prochain scraping réussi)
UNKNOWN_EXPANSION_NAME = "Unknown expansion {id}"


def create_expansions_csv(cardmarket, scrape):
    # La page Cardmarket des extensions est protégée par Cloudflare et peut être inaccessible
    # (IP de serveur bloquée...) : l'import continue alors avec les extensions déjà en base,
    # complétées par create_missing_expansions().
    # Retourne les extensions scrapées (id -> nom), ou None si le CSV n'a pas été généré.
    if not scrape:
        return None
    try:
        return cardmarket.create_expansions_csv()
    except Exception as e:
        logger.warning("Extensions Cardmarket inaccessibles, extensions en base conservées : %s", e)
        return None


def rename_unknown_expansions(db, names):
    # Donne leur vrai nom aux extensions créées sous un nom provisoire.
    # Seules celles qui portent encore exactement ce nom sont modifiées :
    # une extension déjà renommée à la main n'est pas touchée.
    renamed = 0
    for row in db.query("SELECT id, name FROM expansions WHERE name LIKE %s", (UNKNOWN_EXPANSION_NAME.format(id="%"),)):
        placeholder = UNKNOWN_EXPANSION_NAME.format(id=row["id"])
        if row["name"] == placeholder and row["id"] in names:
            db.query("UPDATE expansions SET name = %s WHERE id = %s AND name = %s",
                     (names[row["id"]], row["id"], placeholder))
            renamed += 1
    if renamed:
        logger.info("%d extension(s) provisoire(s) renommée(s) d'après Cardmarket", renamed)


def create_missing_expansions(db, expansion_ids):
    # Crée les extensions utilisées par les produits mais absentes de la base, sous un nom
    # provisoire, pour que les produits ne soient pas refusés par la clé étrangère
    existing = {row["id"] for row in db.query("SELECT id FROM expansions")}
    missing = sorted(expansion_ids - existing)
    for expansion_id in missing:
        db.query("INSERT INTO expansions (id, name) VALUES (%s, %s)",
                 (expansion_id, UNKNOWN_EXPANSION_NAME.format(id=expansion_id)))
    if missing:
        logger.warning("%d extension(s) Cardmarket inconnue(s) créée(s) sous le nom '%s', à renommer : %s",
                       len(missing), UNKNOWN_EXPANSION_NAME.format(id="<id>"), ", ".join(map(str, missing)))


def generate_other_csv(cardmarket, scryfall, scrape_expansions):
    # Génère les CSV autres que les prix (produits et extensions Cardmarket, Scryfall)
    # Retourne (ids des extensions utilisées par les produits, extensions scrapées ou None)
    expansion_ids = cardmarket.create_products_csv()
    scraped_expansions = create_expansions_csv(cardmarket, scrape_expansions)
    scryfall.create_expansions_csv()
    scryfall.create_products_csv()
    return expansion_ids, scraped_expansions


def run_import(db, csv_dir, cardmarket, scryfall, scrape_expansions):
    import_log = ImportLog(db)
    import_log.create_entry()
    try:
        # Les prix d'abord : leur date indique si de nouvelles données sont disponibles,
        # ce qui évite de tout télécharger pour rien
        created_at, date_data = cardmarket.create_prices_csv(import_log.id)
        import_log.set_dates(date_data, created_at)
        if not import_log.is_new_data(created_at):
            import_log.set_status(ImportLog.TOO_EARLY)
            logger.info("Données du %s déjà importées, arrêt", created_at)
            return 1

        expansion_ids, scraped_expansions = generate_other_csv(cardmarket, scryfall, scrape_expansions)

        # Import des CSV dans les tables correspondantes (expansions, products, prices)
        # Sans CSV du jour pour les extensions, un éventuel ancien fichier n'est pas réimporté
        if scraped_expansions is not None:
            db.import_csv_to_table(csv_dir / EXPANSIONS.filename, EXPANSIONS.table, EXPANSIONS.columns)
            rename_unknown_expansions(db, scraped_expansions)
        create_missing_expansions(db, expansion_ids)
        for dataset in (PRODUCTS, PRICES):
            db.import_csv_to_table(csv_dir / dataset.filename, dataset.table, dataset.columns)

        # Partie Scryfall
        # le delete permet de nettoyer les entrées sans ID Cardmarket
        # si scryfall a ajouté des id pour cardmarket alors ils seront importés
        # on ne supprime ainsi pas les ids qui auraient été saisis manuellement
        db.query("DELETE FROM scryfall_products WHERE card_market_id_id IS NULL")
        for dataset in SCRYFALL_DATASETS:
            db.import_csv_to_table(csv_dir / dataset.filename, dataset.table, dataset.columns)

        Matcher(db, csv_dir).run()

        import_log.set_status(ImportLog.FINISHED)
        logger.info("Import terminé")
        return 0
    except Exception:
        import_log.set_status(ImportLog.ERROR)
        logger.error("Erreur pendant l'import, log %s passé en statut \"error\"", import_log.id)
        raise


def main():
    config = load_config()
    setup_logging(config.get('Logging', 'level', fallback='WARNING').upper())
    csv_dir = get_csv_dir(config)
    chrome_version = config.getint('Browser', 'chrome_version', fallback=None)
    scrape_expansions = get_boolean(config, 'Browser', 'scrape_expansions', default=True)

    session = create_session()
    cardmarket = CardmarketSource(session, csv_dir, chrome_version)
    scryfall = ScryfallSource(session, csv_dir)

    # Mode sans base : on télécharge et génère les CSV uniquement (pas de log, pas d'import)
    if not get_boolean(config, 'Database', 'enabled', default=True):
        cardmarket.create_prices_csv()
        generate_other_csv(cardmarket, scryfall, scrape_expansions)
        logger.info("Base désactivée : CSV générés dans %s, rien n'a été importé", csv_dir)
        return 0

    with MySQLConnectionManager.from_config(config) as db:
        return run_import(db, csv_dir, cardmarket, scryfall, scrape_expansions)


if __name__ == "__main__":
    sys.exit(main())
