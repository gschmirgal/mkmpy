import time
from mkmpymysql import dbMkmPy
import mkmpygather


db = dbMkmPy()


mkmpygather.create_product_csv()
mkmpygather.create_expansions_csv()
dateImportFile = mkmpygather.create_prices_csv()

sql = "INSERT INTO logs (dateImport, dateImportFile,status) VALUES ('"+time.strftime('%Y-%m-%d %H:%M:%S')+"', '"+dateImportFile+"', 'OK')"

db.execute_query(sql)

db.import_csv_to_table("csvtemp/expansions_file.csv", "expansions", ";")
db.import_csv_to_table("csvtemp/products_file.csv", "products", ";")
db.import_csv_to_table("csvtemp/prices_file.csv", "prices", ";")