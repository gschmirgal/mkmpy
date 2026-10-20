import logging

import mysql.connector

from mkmpy.csvwriter import DELIMITER

logger = logging.getLogger(__name__)

# Avertissements attendus lors des imports, non affichés :
# - 1062 : ligne déjà présente (imports quotidiens)
# - 1263 : NULL dans une colonne NOT NULL, remplacé par '' ou 0 (ex : cartes sans verso)
EXPECTED_WARNINGS = {1062, 1263}
# Avertissements récurrents et connus, affichés en INFO (pas de mail cron) :
# - 1452 : clé étrangère absente (ex : prix d'un produit absent de la liste des singles)
KNOWN_WARNINGS = {1452}


class MySQLConnectionManager:
    def __init__(self, host, user, password, database, port=3306):
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self.port = port
        self.connection = None

    @classmethod
    def from_config(cls, config):
        config_db = config['Database']
        return cls(
            host=config_db['host'],
            user=config_db['user'],
            password=config_db['password'],
            database=config_db['database'],
            port=config_db.getint('port', fallback=3306),
        )

    def connect(self):
        if self.connection is None or not self.connection.is_connected():
            self.connection = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database,
                port=self.port,
                allow_local_infile=True,  # Nécessaire pour LOAD DATA LOCAL INFILE
                autocommit=True
            )
        return self.connection

    def close(self):
        if self.connection and self.connection.is_connected():
            self.connection.close()
            self.connection = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def query(self, query, params=None):
        # Retourne une liste de dicts si la requête produit des lignes (SELECT, SHOW...),
        # sinon le nombre de lignes affectées
        cursor = self.connect().cursor(dictionary=True)
        try:
            cursor.execute(query, params or ())
            if cursor.with_rows:
                return cursor.fetchall()
            return cursor.rowcount
        finally:
            cursor.close()

    def insert(self, query, params=None):
        # Exécute un INSERT et retourne l'id auto-incrémenté de la ligne créée
        cursor = self.connect().cursor()
        try:
            cursor.execute(query, params or ())
            return cursor.lastrowid
        finally:
            cursor.close()

    def get_value(self, query, params=None):
        # Retourne la première colonne de la première ligne, ou None
        result = self.query(query, params)
        if result:
            return next(iter(result[0].values()))
        return None

    def import_csv_to_table(self, csv_path, table, columns):
        # Importe un CSV écrit par CsvWriter ; les lignes déjà présentes (même clé) sont ignorées
        columns_sql = ", ".join(f"`{column}`" for column in columns)
        inserted = self.query(
            f"LOAD DATA LOCAL INFILE %s IGNORE INTO TABLE `{table}` "
            "CHARACTER SET utf8mb4 "
            f"FIELDS TERMINATED BY '{DELIMITER}' OPTIONALLY ENCLOSED BY '\"' "
            "LINES TERMINATED BY '\\n' "
            f"({columns_sql})",
            (str(csv_path),)
        )
        warnings = self.get_value("SHOW COUNT(*) WARNINGS")
        logger.info("Import %s : %d lignes ajoutées, %d avertissements", table, inserted, warnings)
        # Un exemple par type d'avertissement (MySQL n'en conserve qu'un échantillon)
        examples = {}
        for warning in self.query("SHOW WARNINGS"):
            if warning["Code"] not in EXPECTED_WARNINGS:
                examples.setdefault(warning["Code"], warning["Message"])
        for code, message in examples.items():
            level = logging.INFO if code in KNOWN_WARNINGS else logging.WARNING
            logger.log(level, "Import %s : %s", table, message)
        return inserted
