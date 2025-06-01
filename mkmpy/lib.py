import datetime

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