import logging
import time

import undetected_chromedriver as uc
from bs4 import BeautifulSoup

from mkmpy.csvwriter import CsvWriter
from mkmpy.datasets import EXPANSIONS, PRICES, PRODUCTS
from mkmpy.lib import convert_to_datetime, fetch_json, yesterday

logger = logging.getLogger(__name__)


class CardmarketSource:
    """Récupère produits, prix et extensions Cardmarket et les écrit en CSV."""

    URL_PRICES = "https://downloads.s3.cardmarket.com/productCatalog/priceGuide/price_guide_1.json"
    URL_PRODUCTS = "https://downloads.s3.cardmarket.com/productCatalog/productList/products_singles_1.json"
    URL_EXPANSIONS = "https://www.cardmarket.com/en/Magic/Products/Singles"

    def __init__(self, session, csv_dir, chrome_version=None):
        self.session = session
        self.csv_dir = csv_dir
        self.chrome_version = chrome_version

    def create_products_csv(self):
        # Récupère la liste des produits et écrit un CSV
        data = fetch_json(self.session, self.URL_PRODUCTS)
        with CsvWriter(self.csv_dir / PRODUCTS.filename, PRODUCTS.columns) as writer:
            for product in data["products"]:
                writer.write({column: product.get(key) for column, key in PRODUCTS.fields.items()})
        logger.info("Produits Cardmarket : %d lignes", writer.count)

    def create_prices_csv(self, id_log=None):
        # Récupère les prix et écrit un CSV
        # Retourne (date de génération du fichier, date des données = la veille)
        data = fetch_json(self.session, self.URL_PRICES)
        created_at = convert_to_datetime(data["createdAt"])
        date_data = yesterday(created_at)
        with CsvWriter(self.csv_dir / PRICES.filename, PRICES.columns) as writer:
            for price_guide in data["priceGuides"]:
                row = {column: price_guide.get(key) for column, key in PRICES.fields.items() if key}
                row["date_data"] = date_data.strftime('%Y-%m-%d')
                row["idLog"] = id_log
                writer.write(row)
        logger.info("Prix Cardmarket : %d lignes (fichier du %s)", writer.count, created_at)
        return created_at, date_data

    def create_chrome_driver(self, user_agent=None):
        # Lance Chrome en headless, avec un user-agent forcé si fourni
        options = uc.ChromeOptions()
        if user_agent:
            options.add_argument(f'--user-agent={user_agent}')
        kwargs = {"headless": True}
        if self.chrome_version:
            kwargs["version_main"] = self.chrome_version
        return uc.Chrome(options=options, **kwargs)

    def get_browser_user_agent(self):
        # Récupère le user-agent réel du Chrome installé, sans la mention "Headless"
        # (Cloudflare bloque un UA "HeadlessChrome" ou dont la version ne correspond pas au navigateur)
        driver = self.create_chrome_driver()
        try:
            return driver.execute_script("return navigator.userAgent").replace("HeadlessChrome", "Chrome")
        finally:
            driver.quit()

    def fetch_expansions_select(self, user_agent, timeout):
        # Ouvre la page des extensions et attend la résolution du challenge Cloudflare
        # Retourne le select des extensions, ou None si la page n'est pas accessible
        driver = self.create_chrome_driver(user_agent)
        try:
            driver.get(self.URL_EXPANSIONS)
            start = time.time()
            while time.time() - start < timeout:
                soup = BeautifulSoup(driver.page_source, "html.parser")
                select = soup.find('select', attrs={'name': "idExpansion"})
                if select:
                    return select
                time.sleep(2)
            logger.warning("Extensions : challenge Cloudflare non résolu (page : '%s')", driver.title)
            return None
        finally:
            driver.quit()

    def create_expansions_csv(self, timeout=30, attempts=3):
        # Scrape la page Cardmarket pour récupérer la liste des extensions et écrit un CSV
        # L'UA doit être passé au lancement de Chrome : le modifier ensuite (CDP) ne passe pas Cloudflare
        user_agent = self.get_browser_user_agent()
        select = None
        # Cloudflare bloque parfois une session : on réessaie avec un nouveau navigateur
        for attempt in range(1, attempts + 1):
            select = self.fetch_expansions_select(user_agent, timeout)
            if select:
                break
            logger.warning("Extensions : tentative %d/%d échouée", attempt, attempts)
        if not select:
            raise RuntimeError(f"Liste des extensions introuvable sur {self.URL_EXPANSIONS} après {attempts} tentatives")
        # Extrait les options du select et écrit dans le CSV
        with CsvWriter(self.csv_dir / EXPANSIONS.filename, EXPANSIONS.columns) as writer:
            for option in select.find_all('option'):
                value = option.get('value')
                if value != "0":
                    writer.write({"id": int(value), "name": option.text.strip()})
        logger.info("Extensions Cardmarket : %d lignes", writer.count)
