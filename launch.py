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
from mkmpy.datasets import CARDMARKET_DATASETS, SCRYFALL_DATASETS
from mkmpy.db import MySQLConnectionManager
from mkmpy.import_log import ImportLog
from mkmpy.lib import create_session, get_boolean, get_csv_dir, load_config, setup_logging
from mkmpy.matcher import Matcher
from mkmpy.scryfall import ScryfallSource

logger = logging.getLogger("mkmpy")


def generate_other_csv(cardmarket, scryfall):
    # Génère les CSV autres que les prix (produits et extensions Cardmarket, Scryfall)
    cardmarket.create_products_csv()
    cardmarket.create_expansions_csv()
    scryfall.create_expansions_csv()
    scryfall.create_products_csv()


def run_import(db, csv_dir, cardmarket, scryfall):
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

        generate_other_csv(cardmarket, scryfall)

        # Import des CSV dans les tables correspondantes (expansions, products, prices)
        for dataset in CARDMARKET_DATASETS:
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

    session = create_session()
    cardmarket = CardmarketSource(session, csv_dir, chrome_version)
    scryfall = ScryfallSource(session, csv_dir)

    # Mode sans base : on télécharge et génère les CSV uniquement (pas de log, pas d'import)
    if not get_boolean(config, 'Database', 'enabled', default=True):
        cardmarket.create_prices_csv()
        generate_other_csv(cardmarket, scryfall)
        logger.info("Base désactivée : CSV générés dans %s, rien n'a été importé", csv_dir)
        return 0

    with MySQLConnectionManager.from_config(config) as db:
        return run_import(db, csv_dir, cardmarket, scryfall)


if __name__ == "__main__":
    sys.exit(main())
