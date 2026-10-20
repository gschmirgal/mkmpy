"""
Script de debug pour la récupération des extensions Cardmarket.

Reprend la logique de CardmarketSource.create_expansions_csv() mais :
- affiche chaque étape (création du driver, chargement, titre de page...)
- attend le select en polling (au lieu d'un sleep fixe de 10s)
- sauvegarde le HTML et une capture d'écran dans csvtemp/debug/
- permet de tester avec / sans headless

Usage :
    python debug_expansions.py              # headless (comme en prod)
    python debug_expansions.py --visible    # fenêtre Chrome visible
    python debug_expansions.py --timeout 60
    python debug_expansions.py --ua "Mozilla/5.0 ..."
"""

import argparse
import os
import time
import traceback

import undetected_chromedriver as uc
from bs4 import BeautifulSoup

from mkmpy.lib import load_config

URL = "https://www.cardmarket.com/en/Magic/Products/Singles"
SELECT_NAME = "idExpansion"
DEBUG_DIR = "csvtemp/debug"


def step(msg):
    print(f"[{time.strftime('%H:%M:%S')}] {msg}", flush=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--visible", action="store_true", help="désactive le mode headless")
    parser.add_argument("--timeout", type=int, default=30, help="attente max du select (s)")
    parser.add_argument("--no-ua", action="store_true", help="ne force pas le user-agent")
    parser.add_argument("--ua", help="user-agent à utiliser à la place de celui par défaut")
    parser.add_argument("--auto-ua", action="store_true", help="UA réel du navigateur sans 'Headless' (via CDP)")
    args = parser.parse_args()

    os.makedirs(DEBUG_DIR, exist_ok=True)

    config = load_config()
    chrome_version = config.get("Browser", "chrome_version", fallback=None)
    chrome_version = int(chrome_version) if chrome_version else None
    step(f"undetected_chromedriver {uc.__version__}, chrome_version config = {chrome_version}")

    options = uc.ChromeOptions()
    if args.ua:
        options.add_argument(f'--user-agent={args.ua}')
    elif not args.no_ua and not args.auto_ua:
        options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36')
    kwargs = {"headless": not args.visible}
    if chrome_version:
        kwargs["version_main"] = chrome_version

    step(f"Création du driver {kwargs} ...")
    try:
        driver = uc.Chrome(options=options, **kwargs)
    except Exception:
        step("ECHEC création du driver :")
        traceback.print_exc()
        return

    try:
        if args.auto_ua:
            ua = driver.execute_script("return navigator.userAgent").replace("HeadlessChrome", "Chrome")
            driver.execute_cdp_cmd("Network.setUserAgentOverride", {"userAgent": ua})

        caps = driver.capabilities
        step(f"Chrome {caps.get('browserVersion')} / chromedriver {caps.get('chrome', {}).get('chromedriverVersion', '?').split(' ')[0]}")
        step(f"User-agent effectif : {driver.execute_script('return navigator.userAgent')}")

        step(f"GET {URL}")
        driver.get(URL)

        select = None
        start = time.time()
        while time.time() - start < args.timeout:
            soup = BeautifulSoup(driver.page_source, "html.parser")
            select = soup.find("select", attrs={"name": SELECT_NAME})
            step(f"  t={time.time() - start:4.1f}s  titre='{driver.title}'  select trouvé={select is not None}")
            if select:
                break
            time.sleep(2)

        html_path = os.path.join(DEBUG_DIR, "expansions_page.html")
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(driver.page_source)
        png_path = os.path.join(DEBUG_DIR, "expansions_page.png")
        driver.save_screenshot(png_path)
        step(f"HTML sauvegardé : {html_path}")
        step(f"Capture sauvegardée : {png_path}")

        if not select:
            lower = driver.page_source.lower()
            for marker in ["cloudflare", "just a moment", "cf-challenge", "turnstile", "verify you are human", "access denied"]:
                if marker in lower:
                    step(f"  marqueur détecté dans la page : '{marker}'")
            # Le select a peut-être changé de nom : on liste ceux présents
            for s in soup.find_all("select"):
                step(f"  select présent : name={s.get('name')!r} id={s.get('id')!r} options={len(s.find_all('option'))}")
            step("RESULTAT : select introuvable")
            return

        options_list = [(o.get("value"), o.text.strip()) for o in select.find_all("option") if o.get("value") != "0"]
        step(f"RESULTAT : {len(options_list)} extensions trouvées")
        for value, text in options_list[:5]:
            print(f"    {value} -> {text}")
    finally:
        driver.quit()


if __name__ == "__main__":
    main()
