"""
Script de debug pour la récupération des extensions Cardmarket.

Lance Chrome comme CardmarketSource.create_expansions_csv() (même détection de version,
même user-agent) mais :
- affiche chaque étape (versions, user-agent, titre de la page toutes les 2 s)
- sauvegarde le HTML et une capture d'écran dans csvtemp/debug/
- permet de tester d'autres réglages (mode visible, autre user-agent)

Usage :
    python debug_expansions.py                    # comme en prod (headless, UA réel sans "Headless")
    xvfb-run -a python debug_expansions.py --visible   # Chrome visible (écran virtuel sur un serveur)
    python debug_expansions.py --no-ua            # user-agent propre à Chrome (contient "HeadlessChrome")
    python debug_expansions.py --ua "Mozilla/5.0 ..."
    python debug_expansions.py --timeout 60
"""

import argparse
import os
import time
import traceback

import undetected_chromedriver as uc
from bs4 import BeautifulSoup

from mkmpy.cardmarket import CardmarketSource
from mkmpy.lib import create_session, get_csv_dir, load_config

DEBUG_DIR = "csvtemp/debug"


def step(msg):
    print(f"[{time.strftime('%H:%M:%S')}] {msg}", flush=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--visible", action="store_true", help="désactive le mode headless")
    parser.add_argument("--timeout", type=int, default=30, help="attente max du select (s)")
    parser.add_argument("--no-ua", action="store_true", help="ne force pas le user-agent")
    parser.add_argument("--ua", help="user-agent à utiliser à la place de celui de la prod")
    args = parser.parse_args()

    os.makedirs(DEBUG_DIR, exist_ok=True)

    config = load_config()
    cardmarket = CardmarketSource(create_session(), get_csv_dir(config),
                                  config.getint("Browser", "chrome_version", fallback=None))
    step(f"undetected_chromedriver {uc.__version__}, chrome_version config = {cardmarket.chrome_version}")

    try:
        if args.ua:
            user_agent = args.ua
        elif args.no_ua:
            user_agent = None
        else:
            step("Lecture du user-agent réel de Chrome ...")
            user_agent = cardmarket.get_browser_user_agent()
        step(f"Création du driver (headless={not args.visible}, version={cardmarket.chrome_version}) ...")
        driver = cardmarket.create_chrome_driver(user_agent, headless=not args.visible)
    except Exception:
        step("ECHEC création du driver :")
        traceback.print_exc()
        return

    try:
        caps = driver.capabilities
        step(f"Chrome {caps.get('browserVersion')} / chromedriver {caps.get('chrome', {}).get('chromedriverVersion', '?').split(' ')[0]}")
        step(f"User-agent effectif : {driver.execute_script('return navigator.userAgent')}")

        step(f"GET {cardmarket.URL_EXPANSIONS}")
        driver.get(cardmarket.URL_EXPANSIONS)

        select = None
        start = time.time()
        while time.time() - start < args.timeout:
            soup = BeautifulSoup(driver.page_source, "html.parser")
            select = soup.find("select", attrs={"name": "idExpansion"})
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
