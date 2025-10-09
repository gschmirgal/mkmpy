import mysql.connector
import mkmpy.lib as lib

class MySQLConnectionManager:
    def __init__(self, host, user, password, database, temp= "./", port=3306):
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self.port = port
        self.temp = temp
        self.connection = None

    def connect(self):
        if self.connection is None or not self.connection.is_connected():
            self.connection = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database,
                port=self.port,
                allow_local_infile=True,  # Enables local infile on client side
                autocommit=True           # Optional: ensures autocommit for LOAD DATA
            )
        return self.connection

    def close(self):
        if self.connection and self.connection.is_connected():
            self.connection.close()
            self.connection = None

    def query(self, query, params=None):
        conn = self.connect()
        cursor = conn.cursor(dictionary=True)  # Utilise un curseur qui retourne des dicts
        try:
            cursor.execute(query, params or ())
            if query.strip().lower().startswith("select"):
                result = cursor.fetchall()  # Liste de dicts, indexés par nom de colonne
                return result
            else:
                conn.commit()
                return cursor.rowcount
        finally:
            cursor.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def import_csv_to_table(self, csv_file_path, table_name, delimiter=','):
        query = (
            f"LOAD DATA LOCAL INFILE '{self.temp+csv_file_path}' "
            "IGNORE "
            f"INTO TABLE {table_name} "
            f"FIELDS TERMINATED BY '{delimiter}' "
            "ENCLOSED BY '\"' "
            "LINES TERMINATED BY '\\n' "
            "IGNORE 0 LINES"
        )
        self.query(query)

    def get1value(self, query):
        result = self.query(query)
        if result and len(result) > 0:
            return result[0][next(iter(result[0]))]



class dbMkmPy(MySQLConnectionManager):
    def __init__(self):
        # Create a ConfigParser object
        config = lib.getconfigfile()

        # Access values from the configuration file
        config_db = config['Database']

        super().__init__(
            host=config_db['host'],
            user=config_db['user'],
            password=config_db['password'],
            database=config_db['database'],
            port=config_db['port'],
            temp=config['Folders']['temp']
        )
