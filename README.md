# MKMPy - Cardmarket & Scryfall Data Integration Platform

![Python](https://img.shields.io/badge/Python-3.8+-blue?style=for-the-badge&logo=python&logoColor=white)
![MySQL](https://img.shields.io/badge/MySQL-5.7+-orange?style=for-the-badge&logo=mysql&logoColor=white)
![Selenium](https://img.shields.io/badge/Selenium-4.0+-green?style=for-the-badge&logo=selenium&logoColor=white)
![BeautifulSoup](https://img.shields.io/badge/BeautifulSoup-4.0+-purple?style=for-the-badge&logo=python&logoColor=white)
![Requests](https://img.shields.io/badge/Requests-2.0+-red?style=for-the-badge&logo=python&logoColor=white)

![License](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge)
![Status](https://img.shields.io/badge/Status-Active-brightgreen?style=for-the-badge)
![Magic: The Gathering](https://img.shields.io/badge/Magic%3A%20The%20Gathering-Data%20Integration-blueviolet?style=for-the-badge&logo=wizards-of-the-coast)

## Overview
MKMPy is a comprehensive Python project designed to automate the retrieval, transformation, and integration of Magic: The Gathering product and price data from multiple sources (Cardmarket and Scryfall) into a unified MySQL database. It features advanced data matching algorithms, efficient CSV processing, and maintains bidirectional relationships between different card database systems.

## Features
- **Multi-Source Data Import**: Fetches data from both Cardmarket (JSON API and web scraping) and Scryfall
- **Intelligent Card Matching**: Advanced bidirectional matching system between Scryfall Oracle IDs and Cardmarket meta card IDs
- **Expansion Mapping**: Automatic expansion matching between Scryfall and Cardmarket databases
- **Cloudflare Protection**: Handles Cloudflare-protected pages using undetected_chromedriver
- **Efficient Processing**: Transforms data into clean CSV files with batch processing capabilities
- **Database Integration**: Uses `LOAD DATA LOCAL INFILE` for high-performance MySQL imports
- **Import Logging**: Maintains comprehensive logs of imports with timestamps and status tracking
- **Automated Matching**: Smart algorithm to automatically link unmatched Scryfall products with Cardmarket equivalents

## Requirements
- Python 3.8+
- MySQL server (5.7+ or 8.0+)
- Google Chrome (latest version for undetected_chromedriver)

### Python Packages
Install dependencies with:
```bash
pip install -r requirements.txt
```

**Key Dependencies:**
- `mysql-connector-python` - MySQL database connectivity
- `undetected-chromedriver` - Cloudflare bypass for web scraping
- `requests` - HTTP requests for API calls
- `beautifulsoup4` - HTML parsing for web scraping

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

### Basic Data Import
Run the main script:
```bash
python launch.py
```
This will:
- Download and process product, price, and expansion data from Cardmarket
- Fetch Scryfall data for matching purposes
- Write CSV files to `csvtemp/`
- Import new data into the MySQL database if the last import is older than 1 day
- Log the import in the `logs` table

### Advanced Card Matching
For automatic card matching between Scryfall and Cardmarket databases:
```python
from mkmpy.matcher import matcher

# Initialize matcher (optionally reset Scryfall data)
card_matcher = matcher(reset_scryfall_products=True)

# Run automatic matching process
card_matcher.launchMatching()
```

## Project Structure
```
mkmpy-1/
├── launch.py                 # Main script, orchestrates the workflow
├── mkmpy/
│   ├── gatherer.py          # Data fetching and CSV generation (API and web scraping)
│   ├── db.py                # MySQL connection manager and CSV import logic
│   ├── log.py               # Logging and import control logic
│   ├── lib.py               # Utility functions (implode_quoted, match2ways, etc.)
│   └── matcher.py           # Advanced card matching system (NEW)
├── csvtemp/                 # Output directory for generated CSV files
│   ├── products_file.csv
│   ├── prices_file.csv
│   ├── expansions_file.csv
│   ├── scryfall_products_file.csv
│   └── scryfall_expansions_file.csv
├── requirements.txt         # Python dependencies
├── config_template.ini      # Database configuration template
├── config.ini              # Database configuration (not versioned)
└── sqltables.sql           # SQL schema to initialize the database
```

### Core Modules
- **`matcher.py`** — NEW: Intelligent matching system for Scryfall ↔ Cardmarket relationships
- **`gatherer.py`** — Data fetching and CSV generation (API and web scraping)
- **`db.py`** — MySQL connection manager and CSV import logic
- **`log.py`** — Logging and import control logic
- **`lib.py`** — Utility functions including bidirectional matching algorithms

## Key Features Explained

### Intelligent Card Matching
The `matcher` class provides sophisticated algorithms to:
- Create bidirectional mappings between Scryfall Oracle IDs and Cardmarket meta card IDs
- Match expansions between the two database systems
- Automatically link unmatched Scryfall products with their Cardmarket equivalents
- Handle edge cases where multiple variants exist

### Utility Functions
- **`implode_quoted()`** - SQL-safe string concatenation with proper escaping
- **`match2ways()`** - Creates bidirectional lookup dictionaries for database relationships
- **Batch Processing** - Optimized for handling large datasets efficiently

## Notes
- The project uses undetected_chromedriver to bypass Cloudflare. Make sure Chrome is installed and up to date
- All CSV writing is custom; ensure your data does not contain unescaped semicolons or newlines
- The MySQL user must have `FILE` and `LOCAL INFILE` privileges
- The matching system works best with clean, consistent data from both sources
- Batch processing is implemented for performance optimization on large datasets

## Troubleshooting
- **Undetected ChromeDriver**: Exit errors are harmless and can be ignored
- **CSV Import Issues**: Check CSV quoting and MySQL table column order if columns get mixed
- **Cloudflare Protection**: Increase sleep time in `create_expansions_csv` if blocked
- **Matching Issues**: Ensure both Scryfall and Cardmarket data are properly imported before running matcher
- **Database Connection**: Verify MySQL credentials and permissions in `config.ini`

## Recent Updates
- ✅ **NEW**: Advanced card matching system (`matcher.py`)
- ✅ **NEW**: Bidirectional database relationship mapping
- ✅ **NEW**: Scryfall integration with Oracle ID matching
- ✅ **NEW**: Batch processing optimization for large datasets
- ✅ **NEW**: Enhanced utility functions with SQL injection protection
- ✅ **NEW**: Comprehensive English documentation and code comments
- ✅ **IMPROVED**: Performance optimizations with collections and comprehensions
- ✅ **IMPROVED**: Error handling and data validation

## Contributing
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License
MIT License

---

*Created by Guillaume SCHMIRGAL, 2025.*
