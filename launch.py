"""
MKMPy - Cardmarket Data Importer

Ce projet automatise la récupération, la transformation et l'importation des données produits, prix et extensions Magic: The Gathering depuis Cardmarket vers une base MySQL.

Fonctionnalités principales :
- Récupération de données via API et web scraping (contournement Cloudflare)
- Génération de fichiers CSV intermédiaires
- Import rapide en base MySQL
- Système de log et contrôle d'exécution

Structure :
- mkmpy/db.py : gestion MySQL
- mkmpy/gatherer.py : collecte et génération CSV
- mkmpy/log.py : gestion du log d'import
- mkmpy/lib.py : utilitaires
- launch.py : script principal

Prérequis : voir README.md
"""

from mkmpy.matcher import matcher
from mkmpy.db import dbMkmPy
from mkmpy.gatherer import gatherer
from mkmpy.log import log

# Initialise le système de log et crée une nouvelle entrée de log
log = log()
logId = log.createLogEntry()
try:
    # Initialise le collecteur de données Cardmarket
    mkm = gatherer()

    mkm.set_id_log(logId)

    # Génère les fichiers CSV pour les produits, extensions et prix
    mkm.create_product_csv()
    mkm.create_expansions_csv()
    mkm.create_prices_csv()
    # Génère le fichier CSV pour Scryfall
    mkm.create_scryfall_expansions_csv()
    mkm.create_scryfall_products_csv()

    # Met à jour les date d'importation du fichier dans le log
    log.setdates(mkm.getDateData(), mkm.getDateCreatedAt())

    # Vérifie si l'application peut continuer (ex: pas d'import trop récent)
    if( log.appCanRun() == False ):
        print("App cannot run, exiting")
        exit(1)

    # Initialise la connexion à la base de données
    # et importe les CSV dans les tables correspondantes
    # (expansions, products, prices)
    db = dbMkmPy()
    db.import_csv_to_table("csvtemp/expansions_file.csv", "expansions", ";")
    db.import_csv_to_table("csvtemp/products_file.csv", "products", ";")
    db.import_csv_to_table("csvtemp/prices_file.csv", "prices", ";")

    #partie Scryfall
    #le delete permet de nettoyer les entrées sans ID Cardmarket
    #si scryfall a ajouté des id pour cardmarket alors ils seront importés
    #on ne supprime ainsi pas les ids qui auraient été saisis manuellement
    db.query("DELETE FROM scryfall_products WHERE card_market_id_id IS NULL")
    db.import_csv_to_table("csvtemp/scryfall_expansions_file.csv", "scryfall_expansions", ";")
    db.import_csv_to_table("csvtemp/scryfall_products_file.csv", "scryfall_products", ";")

    match = matcher()
    match.launchMatching()

    # Met à jour le statut du log à "finished"
    log.setStatus("finished")

except Exception as e:
    # En cas d'erreur, met à jour le statut du log à "error" et affiche l'erreur
    log.setStatus("error")
    print(f"An error occurred: {e}")
    raise e