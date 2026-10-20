import gzip
import json
import logging

from mkmpy.csvwriter import CsvWriter
from mkmpy.datasets import SCRYFALL_EXPANSIONS, SCRYFALL_PRODUCTS
from mkmpy.lib import HTTP_TIMEOUT, fetch_json

logger = logging.getLogger(__name__)


def get_nested_value(data, key_string):
    """
    Extrait la valeur d'un dictionnaire imbriqué à partir d'une clé sous forme 'key1.key2.key3'.
    Les entiers indexent les listes ('card_faces.1.name'). Retourne None si la clé n'existe pas.
    """
    value = data
    for key in key_string.split('.'):
        if isinstance(value, dict) and key in value:
            value = value[key]
        elif isinstance(value, list) and key.isdigit() and 0 <= int(key) < len(value):
            value = value[int(key)]
        else:
            return None
    return value


class ScryfallSource:
    """Récupère les sets et les cartes Scryfall et les écrit en CSV."""

    URL_SETS = "https://api.scryfall.com/sets/"
    URL_BULK_INDEX = "https://api.scryfall.com/bulk-data"
    BULK_TYPE = "default_cards"

    def __init__(self, session, csv_dir):
        self.session = session
        self.csv_dir = csv_dir

    def get_bulk_url(self):
        # URL du fichier bulk (jsonl compressé) correspondant à BULK_TYPE
        for bulk in fetch_json(self.session, self.URL_BULK_INDEX)['data']:
            if bulk['type'] == self.BULK_TYPE:
                return bulk['jsonl_download_uri']
        raise RuntimeError(f"Fichier bulk Scryfall '{self.BULK_TYPE}' introuvable")

    def create_products_csv(self):
        # Lit le bulk en flux (sans tout charger en mémoire) et écrit les cartes papier dans un CSV
        response = self.session.get(self.get_bulk_url(), stream=True, timeout=HTTP_TIMEOUT)
        response.raise_for_status()
        with CsvWriter(self.csv_dir / SCRYFALL_PRODUCTS.filename, SCRYFALL_PRODUCTS.columns) as writer:
            with gzip.open(response.raw, "rt", encoding="utf-8") as gz:
                for line in gz:
                    line = line.strip()
                    if not line:
                        continue
                    card = json.loads(line)
                    if 'paper' not in card['games']:
                        continue
                    row = {}
                    for column, key in SCRYFALL_PRODUCTS.fields.items():
                        value = get_nested_value(card, key)
                        # Cartes double face : la valeur est portée par la première face
                        if value is None:
                            value = get_nested_value(card, "card_faces.0." + key)
                        row[column] = value
                    writer.write(row)
        logger.info("Cartes Scryfall : %d lignes", writer.count)

    def create_expansions_csv(self):
        data = fetch_json(self.session, self.URL_SETS)
        with CsvWriter(self.csv_dir / SCRYFALL_EXPANSIONS.filename, SCRYFALL_EXPANSIONS.columns) as writer:
            for ext in data['data']:
                writer.write({column: ext[key] for column, key in SCRYFALL_EXPANSIONS.fields.items()})
        logger.info("Sets Scryfall : %d lignes", writer.count)
