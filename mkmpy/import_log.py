import datetime


class ImportLog:
    """Suivi d'une exécution de l'import dans la table logs (dates et statut)."""

    ONGOING = "ongoing"
    FINISHED = "finished"
    TOO_EARLY = "too early"
    ERROR = "error"

    def __init__(self, db):
        self.db = db
        self.id = None
        self.status = None
        self.date_import = datetime.datetime.now()
        self.date_import_file = None
        self.date_data = None
        # Statuts possibles (table logsteps) : nom -> id
        self.step_ids = {row['step']: row['id'] for row in db.query("SELECT id, step FROM logsteps")}

    def create_entry(self):
        # Crée la ligne de log de l'exécution courante, au statut "ongoing"
        self.status = self.ONGOING
        self.id = self.db.insert(
            "INSERT INTO logs (date_import, idStep) VALUES (%s, %s)",
            (self.date_import, self.step_ids[self.status])
        )
        return self.id

    def set_dates(self, date_data, date_import_file):
        self.date_data = date_data
        self.date_import_file = date_import_file
        self.db.query(
            "UPDATE logs SET date_import_file = %s, date_data = %s WHERE id = %s",
            (date_import_file, date_data.date(), self.id)
        )

    def set_status(self, status):
        if status not in self.step_ids:
            raise ValueError(f"Invalid status: {status}")
        self.status = status
        self.db.query("UPDATE logs SET idStep = %s WHERE id = %s", (self.step_ids[status], self.id))

    def get_last_import_file_date(self):
        # Date du fichier du dernier import terminé, ou None si aucun import n'a abouti
        return self.db.get_value(
            "SELECT MAX(date_import_file) FROM logs WHERE idStep = %s",
            (self.step_ids[self.FINISHED],)
        )

    def is_new_data(self, date_import_file):
        # Vrai si le fichier est plus récent que celui du dernier import terminé
        last = self.get_last_import_file_date()
        return last is None or date_import_file > last
