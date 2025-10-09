import configparser
import datetime
import os

# Convertit une chaîne de caractères en objet datetime.datetime si possible.
# Accepte les formats ISO (ex: '2025-06-01T12:34:56') ou 'YYYY-MM-DD'.
def convert_to_datetime(date_str):
    if isinstance(date_str, str):
        try:
            date_str = datetime.datetime.strptime(date_str[:-5], "%Y-%m-%dT%H:%M:%S")
        except ValueError:
            try:
                date_str = datetime.datetime.strptime(date_str, "%Y-%m-%d")
            except ValueError:
                print(f"Could not parse dateImportFile: {date_str}")
                date_str = None
    return date_str

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

def getconfigfile():
    if os.path.exists("../config.ini"):
        config_file = "../config.ini"
    else:
        config_file = "config.ini"
        
    config = configparser.ConfigParser()

    # Read the configuration file
    config.read(config_file)
    return config  # Retourner l'objet config, pas le résultat de read()