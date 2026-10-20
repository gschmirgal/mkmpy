import csv

DELIMITER = ";"


def format_value(value):
    # Adapte une valeur Python au format attendu par LOAD DATA (échappement par défaut '\')
    if value is None:
        return r"\N"                            # NULL
    if isinstance(value, bool):
        return int(value)                       # tinyint 0/1
    if isinstance(value, str):
        return value.replace("\\", "\\\\")      # un '\' littéral doit être doublé
    return value


class CsvWriter:
    """
    Écrit un CSV correspondant à un Dataset, lisible par MySQLConnectionManager.import_csv_to_table().
    Les lignes sont des dicts indexés par nom de colonne ; les colonnes absentes valent NULL.

        with CsvWriter(csv_dir / PRODUCTS.filename, PRODUCTS.columns) as writer:
            writer.write({"id": 1, "name": "Arrest", ...})
    """

    def __init__(self, path, columns):
        self.path = path
        self.columns = columns
        self.count = 0
        self._file = None
        self._writer = None

    def __enter__(self):
        self._file = open(self.path, "w", encoding="utf-8", newline="")
        self._writer = csv.writer(self._file, delimiter=DELIMITER, quotechar='"', lineterminator="\n")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._file.close()

    def write(self, row):
        self._writer.writerow([format_value(row.get(column)) for column in self.columns])
        self.count += 1
