# MKMPy - Cardmarket Data Importer

## Overview
MKMPy is a Python project designed to automate the retrieval, transformation, and import of Magic: The Gathering product and price data from Cardmarket into a MySQL database. It handles both API-based and web-scraped data, processes it into CSV files, and loads it efficiently into your database for further analysis or integration.

## Features
- Fetches product, price, and expansion data from Cardmarket (JSON API and web scraping).
- Handles Cloudflare-protected pages using undetected_chromedriver.
- Transforms data into clean CSV files.
- Efficiently imports CSV data into MySQL using `LOAD DATA LOCAL INFILE`.
- Maintains a log of imports with timestamps and status.

## Requirements
- Python 3.8+
- MySQL server
- Google Chrome (for undetected_chromedriver)

### Python Packages
Install dependencies with:
```
pip install -r requirements.txt
```

## Database Initialization
Before running the project, you **must initialize your MySQL database** using the provided SQL schema:

1. Open your MySQL client (Workbench, command line, etc.).
2. Import the file `sqltables.sql` to create the necessary tables and structure:
   ```sql
   SOURCE path/to/sqltables.sql;
   ```
   Or, from the command line (PowerShell):
   ```powershell
   mysql -u youruser -p yourdb < sqltables.sql
   ```

## Configuration
1. Copy `config_template.ini` to `config.ini` and fill in your MySQL credentials:
   ```ini
   [Database]
   host=localhost
   user=youruser
   password=yourpassword
   database=yourdb
   port=3306
   ```
2. Ensure the `csvtemp/` directory exists (for CSV output).

## Usage
Run the main script:
```
python launch.py
```
This will:
- Download and process product, price, and expansion data.
- Write CSV files to `csvtemp/`.
- Import new data into the MySQL database if the last import is older than 1 day.
- Log the import in the `logs` table.

## Project Structure
- `launch.py` — Main script, orchestrates the workflow.
- `mkmpy/gatherer.py` — Data fetching and CSV generation (API and web scraping).
- `mkmpy/db.py` — MySQL connection manager and CSV import logic.
- `mkmpy/log.py` — Logging and import control logic.
- `mkmpy/lib.py` — Utility functions.
- `csvtemp/` — Output directory for generated CSV files.
- `requirements.txt` — Python dependencies.
- `config.ini` — Database configuration (not versioned, use `config_template.ini`).
- `sqltables.sql` — SQL schema to initialize the database (must be imported before first use).

## Notes
- The project uses undetected_chromedriver to bypass Cloudflare. Make sure Chrome is installed and up to date.
- All CSV writing is custom; ensure your data does not contain unescaped semicolons or newlines.
- The MySQL user must have `FILE` and `LOCAL INFILE` privileges.

## Troubleshooting
- If you see errors related to undetected_chromedriver at exit, they are harmless and can be ignored.
- If CSV import mixes columns, check your CSV quoting and the MySQL table column order.
- For Cloudflare issues, try increasing the sleep time in `create_expansions_csv`.

## License
MIT License

---

*Created by gilom, 2025.*
