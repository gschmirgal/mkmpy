import datetime
from mkmpy.db import dbMkmPy

class log:
    db = dbMkmPy()
    statuses = {}
    statusesFlip = {}
    id = None
    dateImport = datetime.datetime.now()
    dateImportFile = None
    dateData = None
    status = "ongoing"
    
    def __init__(self):
        db = dbMkmPy()
        self.statuses = self.getStatuses()
        self.statusesFlip = {v: k for k, v in self.statuses.items()}

    def getStatuses(self):
        datadb = self.db.query("SELECT * FROM logsteps WHERE 1")
        data = {}
        for row in datadb:
            data[row['id']] = row['step']
        return data

    def createLogEntry(self):
        sql = f"INSERT INTO logs (dateImport, idStep) VALUES ('{self.dateImport.strftime('%Y-%m-%d %H:%M:%S')}', '{self.statusesFlip[self.status]}')"
        self.db.query(sql)

        self.id = self.db.get1value("SELECT LAST_INSERT_ID()")
        return self.id
    

    def setdates(self, dateData, dateImportFile):
        self.dateImportFile = dateImportFile
        self.dateData = dateData
    
        sql = f"""UPDATE logs 
        SET dateImportFile = '{self.dateImportFile.strftime('%Y-%m-%d %H:%M:%S')}',
        dateData = '{self.dateData.strftime('%Y-%m-%d')}' 
        WHERE id = {self.id}"""
        self.db.query(sql)

    def setStatus(self, status):
        if status not in self.statuses.values():
            raise ValueError(f"Invalid status: {status}")
        
        self.status = status
        
        sql = f"UPDATE logs SET idStep = '{self.statusesFlip[self.status]}' WHERE id = {self.id}"
        self.db.query(sql)
    
    def appCanRun(self):
        sql = "SELECT max(dateImportFile) FROM logs WHERE idStep = '50' "
        lastDateImpoFile = self.db.get1value(sql)

        if( lastDateImpoFile >= self.dateImportFile ):
            self.setStatus("too early")
            return False
        else:
            return True

        