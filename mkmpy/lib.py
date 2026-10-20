import configparser
import datetime
import logging
from pathlib import Path

import requests

PROJECT_ROOT = Path(__file__).resolve().parent.parent

USER_AGENT = "mkmpy/1.0 (https://github.com/gschmirgal/mkmpy)"
HTTP_TIMEOUT = 60  # secondes, appliqué à la connexion et à chaque lecture


def load_config(path=None):
    # Lit le config.ini à la racine du projet, quel que soit le dossier courant
    config_path = Path(path) if path else PROJECT_ROOT / "config.ini"
    config = configparser.ConfigParser()
    if not config.read(config_path, encoding="utf-8"):
        raise FileNotFoundError(f"Fichier de configuration introuvable : {config_path}")
    return config


def get_boolean(config, section, key, default):
    # Comme config.getboolean, mais une clé absente ou vide vaut default
    if not config.get(section, key, fallback="").strip():
        return default
    return config.getboolean(section, key)


def get_csv_dir(config):
    # Dossier des CSV ; un chemin relatif dans le config est résolu depuis la racine du projet
    return PROJECT_ROOT / config.get('Folders', 'temp', fallback='./') / "csvtemp"


def setup_logging(level="WARNING"):
    # level : nom de niveau logging (INFO, WARNING...) ; en WARNING une exécution normale n'affiche rien
    logging.basicConfig(level=level, format="%(asctime)s %(levelname)-7s %(name)s - %(message)s", datefmt="%H:%M:%S")
    logging.getLogger("undetected_chromedriver").setLevel(logging.WARNING)


def create_session():
    # Session HTTP partagée, avec un user-agent identifiant le projet (demandé par Scryfall)
    session = requests.Session()
    session.headers["User-Agent"] = USER_AGENT
    return session


def fetch_json(session, url):
    # Télécharge et parse un JSON ; les erreurs HTTP et de parsing remontent à l'appelant
    response = session.get(url, timeout=HTTP_TIMEOUT)
    response.raise_for_status()
    return response.json()


# Convertit une date ISO (ex: '2025-06-01T12:34:56+0200' ou '2025-06-01') en datetime.
# Le fuseau horaire est ignoré : les dates sont stockées sans fuseau en base.
def convert_to_datetime(value):
    if not isinstance(value, str):
        return value
    try:
        return datetime.datetime.fromisoformat(value).replace(tzinfo=None)
    except ValueError:
        raise ValueError(f"Date non reconnue : {value!r}")


# Retourne la date de la veille par rapport à la date passée en paramètre.
def yesterday(date):
    return date - datetime.timedelta(days=1)


def implode_quoted(separator, array, quote="'"):
    quoted_items = []
    for item in array:
        escaped = str(item).replace(quote, quote + quote)
        quoted_items.append(f"{quote}{escaped}{quote}")
    return separator.join(quoted_items)

#warning, only use with very different matchig
#like int id and string 32 id for example
def match2ways( data ):
    indexed = {}
    for row in data:
        valeurs = list(row.values())
        a = valeurs[0]
        b = valeurs[1]

        if a not in indexed:
            indexed[a] = []

        if b not in indexed:
            indexed[b] = []
        indexed[a].append(b)
        indexed[b].append(a)

    for row in indexed:
        indexed[row] = list(set(indexed[row]))

    return indexed
