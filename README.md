# MKMPy

![Python](https://img.shields.io/badge/Python-3.12+-blue?logo=python&logoColor=white)
![MySQL](https://img.shields.io/badge/MySQL-8.0-orange?logo=mysql&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-yellow)

Daily import of Magic: The Gathering data from **Cardmarket** (products, expansions, price guide) and **Scryfall** (sets, cards) into a MySQL database, with automatic linking of Scryfall cards to their Cardmarket products.

## How it works

Each run of `launch.py`:

1. Downloads the Cardmarket price guide and stops if it is not newer than the last finished import.
2. Downloads the other sources and writes one CSV file per table in `csvtemp/`:
   - Cardmarket products: public JSON file
   - Cardmarket expansions: scraped from the Singles page with a headless Chrome (the page is behind Cloudflare). If the page cannot be reached, the import continues with the expansions already in the database
3. Creates the expansions used by the products but missing from the database, named `Unknown expansion <id>`: rename them by hand, or they are renamed on the next successful scraping
   - Scryfall sets and cards: Scryfall API and `default_cards` bulk file (paper cards only)
4. Imports the CSV files with `LOAD DATA LOCAL INFILE`. Rows that already exist are skipped, so products and expansions accumulate over time and prices are added for each day.
5. Runs the matching: Scryfall cards without a Cardmarket id are linked when the link can be deduced unambiguously from the cards already linked (same card, same expansion).
6. Records the run in the `logs` table with its status: `ongoing`, `finished`, `too early` or `error`.

The database can be disabled to only produce the CSV files (see [Configuration](#configuration)).

## Requirements

- Python 3.12+
- Google Chrome
- MySQL 8.0 with `local_infile` enabled on the server (not needed when the database is disabled)

## Installation

```bash
python -m venv .venv
.venv/bin/pip install -r requirements.txt
cp config_template.ini config.ini
```

Then create the tables:

```bash
mysql -u youruser -p yourdb < sqltables.sql
```

## Configuration

`config.ini` is read from the project root.

```ini
[Database]
# false: download the data and write the CSV files only (no MySQL, no log, no matching)
enabled  = true
host     = 127.0.0.1
user     = mkmpy
password = your_password
database = mkmpy
port     = 3306

[Folders]
# folder containing csvtemp/, relative to the project root
temp     = ./

[Logging]
# WARNING: a normal run prints nothing; INFO: full progress
level    = WARNING

[Browser]
# false: skip the Cardmarket expansions page; new expansions are created as "Unknown expansion <id>"
scrape_expansions = true
# force the ChromeDriver major version (detected automatically on Linux/macOS)
# chrome_version = 149
```

`enabled` defaults to `true` and `level` to `WARNING` when they are missing.

## Usage

```bash
.venv/bin/python launch.py
```

Exit code is `0` on success and `1` when the data was already imported. With `level = WARNING`, a normal run produces no output, so it can be scheduled with cron and only send a mail when something goes wrong:

```cron
0 6 * * * cd /path/to/mkmpy && .venv/bin/python launch.py
```

Warnings are printed for unexpected MySQL warnings during an import, when the expansions page cannot be scraped (see [Cloudflare](#cloudflare-and-the-expansions-page)), when unknown expansions are created and for errors.

## Project structure

```
launch.py               Entry point
mkmpy/
  cardmarket.py         CardmarketSource: products, prices, expansions -> CSV
  scryfall.py           ScryfallSource: sets, cards -> CSV
  datasets.py           Target tables and source field -> column mapping
  csvwriter.py          CSV writer compatible with LOAD DATA
  db.py                 MySQL connection and CSV import
  import_log.py         ImportLog: runs tracking in the logs table
  matcher.py            Matcher: Scryfall / Cardmarket linking
  lib.py                Configuration, HTTP and helpers
tests/                  Unit tests
debug_expansions.py     Diagnostic tool for the expansions scraping
sqltables.sql           Database schema
```

The column order of each table is defined once in `datasets.py` and used both to write the CSV file and in the `LOAD DATA` column list.

## Matching only

The matching can be run on its own, for example after fixing links by hand:

```python
from mkmpy.db import MySQLConnectionManager
from mkmpy.lib import get_csv_dir, load_config
from mkmpy.matcher import Matcher

config = load_config()
with MySQLConnectionManager.from_config(config) as db:
    # reset_scryfall_products=True reloads scryfall_products from its CSV file first
    Matcher(db, get_csv_dir(config)).run()
```

Links already present in `scryfall_products.card_market_id_id`, including the ones set by hand, are kept across imports.

## Troubleshooting

- **Expansions page blocked**: see [Cloudflare and the expansions page](#cloudflare-and-the-expansions-page).
- **`session not created: cannot connect to chrome`**: the ChromeDriver does not match the installed Chrome. The version is detected automatically on Linux/macOS; on Windows, or if detection fails, set `chrome_version` in `[Browser]` to the major version of Chrome.
- **`LOAD DATA LOCAL INFILE` refused**: enable `local_infile` on the MySQL server.
- **Prices rejected during the import**: the price guide contains products that are not in the Singles product list. They are skipped because of the foreign key on `products` (shown with `level = INFO`).

## Cloudflare and the expansions page

The Cardmarket products and price guide are JSON files served without protection, but the expansion names are only available on the Singles page, which is behind Cloudflare. It is scraped with [undetected-chromedriver](https://github.com/ultrafunkamsterdam/undetected-chromedriver).

What is needed for the scraping to pass:
- **A consistent user-agent**: Cloudflare blocks a user-agent containing `HeadlessChrome` or announcing another Chrome version than the real one. The code reads the real user-agent of the installed Chrome, removes `Headless` and passes it at launch (changing it afterwards through CDP is not enough).
- **A ChromeDriver matching Chrome**: undetected-chromedriver downloads the latest ChromeDriver by default, which does not start when Chrome is not up to date yet. The installed version is detected and passed to it.
- **An IP that Cloudflare trusts**: from some servers (cloud/VPS IPs), Cloudflare always shows an interactive "Verify you are human" checkbox, in headless or visible mode (Xvfb). This is a deliberate protection and the project does not try to get around it.

When the page cannot be scraped (3 attempts):
- the import continues with the expansions already in the database, with a warning;
- expansions used by the products but missing from the database are created as `Unknown expansion <id>`, and a warning lists them, so a cron mail is sent once per new expansion;
- rename them by hand: `UPDATE expansions SET name = '...' WHERE id = <id>`. Expansions still named exactly `Unknown expansion <id>` are renamed automatically on the next successful scraping; the ones renamed by hand are left untouched.

On a server that always gets the checkbox, set `scrape_expansions = false` in `[Browser]`: Chrome is not started and normal runs stay silent.

To diagnose, run `python debug_expansions.py`. It prints the Chrome and ChromeDriver versions, the user-agent and the page title every 2 seconds, and saves the page HTML and a screenshot in `csvtemp/debug/`. Options: `--visible` (no headless, use `xvfb-run -a` on a server), `--no-ua` (Chrome's own user-agent), `--ua "<user-agent>"`, `--timeout <seconds>`.

## Tests

```bash
.venv/bin/python -m unittest discover -s tests -t .
```

## License

MIT

---

*Created by Guillaume SCHMIRGAL, 2025.*
