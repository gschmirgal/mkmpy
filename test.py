from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import undetected_chromedriver as uc
from bs4 import BeautifulSoup
import time
import requests

def fetch_and_parse_json(url):
    try:
        # Télécharger le JSON depuis l'URL
        response = requests.get(url)
        response.raise_for_status()  # Vérifie les erreurs HTTP
        return response.json()  # Convertir la réponse en JSON
    
    except requests.exceptions.RequestException as e:
        print(f"Erreur lors du téléchargement : {e}")
    except ValueError as e:
        print(f"Erreur lors de la conversion en JSON : {e}")

def csvify(values):
    return '"'+'";"'.join(str(x) for x in values.values()) + '"\n'


def create_product_csv():
    url = "https://downloads.s3.cardmarket.com/productCatalog/productList/products_singles_1.json"  
    data = fetch_and_parse_json(url)

    createdAt = data.get("createdAt")
    products = data.get("products")

    
    f_products = open("csvtemp/products_file.csv", "w", encoding="utf-8")

    for product in products:
        product.pop("categoryName")
        product.pop("idCategory")
        f_products.write( csvify(product) )


def create_prices_csv():
    url = "https://downloads.s3.cardmarket.com/productCatalog/priceGuide/price_guide_1.json"  
    data = fetch_and_parse_json(url)

    createdAt = data.get("createdAt")
    priceGuides = data.get("priceGuides")

    
    f_prices = open("csvtemp/prices_file.csv", "w", encoding="utf-8")

    for priceGuide in priceGuides:
        priceGuide.pop("idCategory")
        priceGuide["date"] = createdAt
        f_prices.write( csvify( priceGuide ))

def create_expansions_csv():
    url = "https://www.cardmarket.com/fr/Magic/Products/Singles"
    name = "idExpansion"
    
    f_expansions = open("csvtemp/expansions_file.csv", "w", encoding="utf-8")

    options = uc.ChromeOptions()
    options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36')
    driver = uc.Chrome(options=options, headless=True)

    driver.get(url)

    # Wait for Cloudflare challenge (increase if needed)
    time.sleep(10)

    html = driver.page_source
    soup = BeautifulSoup(html, "html.parser")
    select = soup.find('select', attrs={'name': name})
    if not select:
        return []
    # Extraire les options du select
    for option in select.find_all('option'):
        value = option.get('value')
        text = option.text.strip()
        #f_expansions.write( '"' + value + '";"' + text + '"\n')
        if value != "0":
            f_expansions.write( csvify( {1:value, 2:text} ) )


    driver.quit()




create_product_csv()
create_prices_csv()
create_expansions_csv()