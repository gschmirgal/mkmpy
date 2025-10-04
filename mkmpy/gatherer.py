import undetected_chromedriver as uc
from bs4 import BeautifulSoup
import time
import requests
from mkmpy.lib import convert_to_datetime, yesterday

class gatherer:
    def __init__(self):
        # URLs pour récupérer les données produits, prix et extensions
        self.urlPrices          = "https://downloads.s3.cardmarket.com/productCatalog/priceGuide/price_guide_1.json"
        self.urlProducts        = "https://downloads.s3.cardmarket.com/productCatalog/productList/products_singles_1.json"
        self.urlExpansions      = "https://www.cardmarket.com/en/Magic/Products/Singles"

        self.urlIndexScryfall   = "https://api.scryfall.com/bulk-data"
        self.scryfallType       = "default_cards"

        self.createdAt      = None  # Date de création des données par mkm
        self.dateData       = None  # Date des données (utilisée pour les prix)

        self.idLog          = 0     # Identifiant de log pour le suivi

    def set_id_log(self, idLog):
        # Définit l'identifiant de log
        self.idLog = idLog

    def getDateData(self):
        # Retourne la date des données
        return self.dateData
    
    def getDateCreatedAt(self):
        # Retourne la date de création des données
        return self.createdAt

    def fetch_and_parse_json(self,url):
        # Télécharge et parse un JSON depuis une URL
        try:
            response = requests.get(url)
            response.raise_for_status()  # Vérifie les erreurs HTTP
            return response.json()  # Convertir la réponse en JSON
        except requests.exceptions.RequestException as e:
            print(f"Erreur lors du téléchargement : {e}")
        except ValueError as e:
            print(f"Erreur lors de la conversion en JSON : {e}")

    def csvify(self,values):
        # Transforme un dictionnaire de valeurs en ligne CSV, avec gestion des types et des guillemets
        csvline = ""
        for key in values:
            if values[key] is None:
                csvline += 'NULL;'
            elif( isinstance(values[key], int) or isinstance(values[key], float) or values[key].isnumeric()  ):
                csvline += f'{values[key]};'
            else:
                csvline += f'"{str(values[key]).replace("\"", "\"\"")}";'
        return f'{csvline}\n'


    def create_product_csv(self):
        # Récupère la liste des produits et écrit un CSV
        data = self.fetch_and_parse_json(self.urlProducts)
        createdAt = convert_to_datetime(data.get("createdAt"))
        products = data.get("products")
        with open("csvtemp/products_file.csv", "w", encoding="utf-8") as f_products:
            for product in products:
                newProduct = {}
                for key in ["idProduct", "name", "idMetacard", "dateAdded", "idExpansion"]:
                    if key not in product:
                        product[key] = None
                    newProduct[key] = product[key]
                f_products.write(self.csvify(newProduct))
        return createdAt


    def create_prices_csv(self):
        # Récupère les prix, ajoute des champs, et écrit un CSV
        data = self.fetch_and_parse_json(self.urlPrices)
        self.createdAt = convert_to_datetime(data.get("createdAt"))
        self.dateData = yesterday(self.createdAt)
        dateDataStr = self.dateData.strftime('%Y-%m-%d')
        priceGuides = data.get("priceGuides")
        with open("csvtemp/prices_file.csv", "w", encoding="utf-8") as f_prices:
            for priceGuide in priceGuides:
                newPriceGuide = {"id": 0}
                priceGuide["idLog"] = self.idLog
                priceGuide["dataDate"] = dateDataStr
                for key in ["dataDate", "avg", "low", "trend", "avg1", "avg7", "avg30", "avg-foil", "low-foil", "trend-foil", "avg1-foil", "avg7-foil", "avg30-foil", "idProduct", "idLog"]:
                    if key not in priceGuide:
                        priceGuide[key] = None
                    newPriceGuide[key] = priceGuide[key]
                f_prices.write(self.csvify(newPriceGuide))
        return self.createdAt

    def create_expansions_csv(self):
        # Scrape la page Cardmarket pour récupérer la liste des extensions et écrit un CSV
        name = "idExpansion"
        with open("csvtemp/expansions_file.csv", "w", encoding="utf-8") as f_expansions:
            options = uc.ChromeOptions()
            options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36')
            driver = uc.Chrome(options=options, headless=True)
            try:
                driver.get(self.urlExpansions)
                # Attend le challenge Cloudflare
                time.sleep(10)
                html = driver.page_source
                soup = BeautifulSoup(html, "html.parser")
                select = soup.find('select', attrs={'name': name})
                if not select:
                    return 0
                # Extrait les options du select et écrit dans le CSV
                for option in select.find_all('option'):
                    value = option.get('value')
                    text = option.text.strip()
                    if value != "0":
                        f_expansions.write(self.csvify({1: value, 2: text}))
            finally:
                driver.quit()
        return 1
    
    def getScryfallUrl(self):
        urls = self.fetch_and_parse_json(self.urlIndexScryfall)

        for url in urls['data']:
            if( url['type'] == self.scryfallType ):
                return url['download_uri']
            
        return None
    
    def create_scryfall_products_csv(self):
        url = self.getScryfallUrl()
        if not url:
            print("No Scryfall URL found for the specified type.")
            return
        
        scryfallData = self.fetch_and_parse_json(url)

        with open("csvtemp/scryfall_products_file.csv", "w", encoding="utf-8") as f_scryfall:
            for card in scryfallData:
                line = {}
                if 'paper' not in card['games']:
                    continue
                for key in ["id",
                            "cardmarket_id",
                            "oracle_id",
                            "image_uris.normal",
                            "image_uris.png",
                            "reserved",
                            "set_id",
                            "name",
                            "card_faces.1.image_uris.normal",
                            "card_faces.1.image_uris.png",
                            "collector_number",
                            "rarity",
                            "related_uris.gatherer",
                            "scryfall_uri"]:
                    value = self.get_nested_value(card, key)
                    if value is None:
                        value = self.get_nested_value(card, "card_faces.0."+key)
                    line[key] = value

                f_scryfall.write(self.csvify(line))
        return True
    
    def create_scryfall_expansions_csv(self):

        scryfallData = self.fetch_and_parse_json("https://api.scryfall.com/sets/")

        with open("csvtemp/scryfall_expansions_file.csv", "w", encoding="utf-8") as f_scryfall:
            for ext in scryfallData['data']:
                line = {}
                for key in ["id",
                            "code",
                            "name",
                            "icon_svg_uri"]:
                   line[key] = ext[key]

                f_scryfall.write(self.csvify(line))
        return True

    def get_nested_value(self, data, key_string):
        """
        Extrait la valeur d'un dictionnaire imbriqué à partir d'une clé sous forme 'key1.key2.key3'.
        Retourne None si la clé n'existe pas.
        """
        keys = key_string.split('.')
        value = data
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            elif isinstance(value, list) and key.isdigit() and 0 <= int(key) < len(value):
                value = value[int(key)]
            else:
                return None
        return value