"""
Description des jeux de données importés : table MySQL cible et correspondance
colonne de la table -> clé dans les données source.

C'est la seule source de vérité pour l'ordre des colonnes : les CSV sont écrits
dans cet ordre et LOAD DATA reçoit la même liste de colonnes.
Une clé source à None signifie que la valeur est calculée par le code.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class Dataset:
    table: str
    fields: dict  # colonne de la table -> clé source

    @property
    def columns(self):
        return tuple(self.fields)

    @property
    def filename(self):
        return f"{self.table}_file.csv"


EXPANSIONS = Dataset("expansions", {
    "id": None,     # value de l'option du select Cardmarket
    "name": None,   # texte de l'option
})

PRODUCTS = Dataset("products", {
    "id": "idProduct",
    "name": "name",
    "id_meta_card": "idMetacard",
    "date_added": "dateAdded",
    "idExpansion": "idExpansion",
})

PRICES = Dataset("prices", {
    "date_data": None,  # veille de la date de génération du fichier
    "avg": "avg",
    "low": "low",
    "trend": "trend",
    "avg1": "avg1",
    "avg7": "avg7",
    "avg30": "avg30",
    "avg_foil": "avg-foil",
    "low_foil": "low-foil",
    "trend_foil": "trend-foil",
    "avg1_foil": "avg1-foil",
    "avg7_foil": "avg7-foil",
    "avg30_foil": "avg30-foil",
    "idProduct": "idProduct",
    "idLog": None,      # id de l'import en cours
})

SCRYFALL_EXPANSIONS = Dataset("scryfall_expansions", {
    "id": "id",
    "code": "code",
    "name": "name",
    "icon_svg_uri": "icon_svg_uri",
})

# Les clés pointées ('a.b.0.c') désignent des valeurs imbriquées
SCRYFALL_PRODUCTS = Dataset("scryfall_products", {
    "id": "id",
    "card_market_id_id": "cardmarket_id",
    "oracle_id": "oracle_id",
    "img_normal_uri": "image_uris.normal",
    "img_png_uri": "image_uris.png",
    "reserved": "reserved",
    "scryfall_expansion_id": "set_id",
    "name": "name",
    "img_normal_uri_back": "card_faces.1.image_uris.normal",
    "img_png_uri_back": "card_faces.1.image_uris.png",
    "collector_number": "collector_number",
    "rarity": "rarity",
    "gatherer_uri": "related_uris.gatherer",
    "scryfall_uri": "scryfall_uri",
})

# Ordre d'import imposé par les clés étrangères
CARDMARKET_DATASETS = (EXPANSIONS, PRODUCTS, PRICES)
SCRYFALL_DATASETS = (SCRYFALL_EXPANSIONS, SCRYFALL_PRODUCTS)
