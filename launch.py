import datetime
from mkmpymysql import dbMkmPy
import mkmpygather

mkmpygather.create_product_csv()
mkmpygather.create_expansions_csv()
dateImportFile = mkmpygather.create_prices_csv()

db = dbMkmPy()

sql = "SELECT max(dateImportFile) FROM logs WHERE status = 'OK'"
lastDateImportFile = db.execute_query(sql)

now = datetime.datetime.now()

yesterday = (now - datetime.timedelta(days=1))

if lastDateImportFile[0][0] > yesterday:
    print("Nothing to do, last import is recent")
    sql = f"INSERT INTO logs (dateImport, dateImportFile,status) VALUES ('{now.strftime('%Y-%m-%d %H:%M:%S')}', '{dateImportFile}', 'too early')"
    db.execute_query(sql)
    exit(0)

sql = f"INSERT INTO logs (dateImport, dateImportFile,status) VALUES ('{now.strftime('%Y-%m-%d %H:%M:%S')}', '{dateImportFile}', 'OK')"
db.execute_query(sql)

db.import_csv_to_table("csvtemp/expansions_file.csv", "expansions", ";")
db.import_csv_to_table("csvtemp/products_file.csv", "products", ";")
db.import_csv_to_table("csvtemp/prices_file.csv", "prices", ";")