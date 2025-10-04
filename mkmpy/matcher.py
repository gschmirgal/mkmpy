import os
from mkmpy import db
from mkmpy.db import dbMkmPy
from mkmpy.lib import implode_quoted, match2ways

class matcher:
    """
    Card matching class that handles the relationship between Scryfall and CardMarket (MKM) data.
    This class creates and maintains bidirectional mappings between the two card databases.
    """
    db = dbMkmPy()
    
    def __init__(self, reset_scryfall_products=False):
        """Initialize the matcher and gather all matching data."""
        if  reset_scryfall_products:
            self.resetScryfallProducts()
        self.gatherdata()

    def gatherdata(self):
        """
        Main data gathering method that builds both expansion and card matching tables.
        This method coordinates the creation of all necessary matching relationships.
        """
        self.generateExpansionMatching()
        self.generateCardsMatching()

    def resetScryfallProducts(self):
        """
        Reset and reimport Scryfall products data from CSV file.
        This method clears the scryfall_products table and reloads it from the CSV file.
        Only executes if the CSV file exists in the csvtemp directory.
        """
        if os.path.exists("csvtemp/scryfall_products_file.csv"):
            # Disable foreign key checks to allow truncation
            self.db.query("SET FOREIGN_KEY_CHECKS = 0;")
            self.db.query("TRUNCATE TABLE scryfall_products;")
            self.db.query("SET FOREIGN_KEY_CHECKS = 1;")

            # Reimport clean data
            self.db.import_csv_to_table("csvtemp/scryfall_products_file.csv", "scryfall_products", ";")

    def generateExpansionMatching(self):
        """
        Generate bidirectional expansion matching between Scryfall and CardMarket.
        This method creates the expansions_matching table and builds a lookup dictionary
        for quick expansion ID translation between the two systems.
        """
        # Clear the matching table
        self.db.query("TRUNCATE TABLE expansions_matching;")

        sql = """
            INSERT INTO expansions_matching 
            SELECT DISTINCT 0, cm_e.id, sf_e.id
            FROM scryfall_products sf_p 
            INNER JOIN products cm_p ON sf_p.card_market_id_id = cm_p.id
            INNER JOIN scryfall_expansions sf_e ON sf_p.scryfall_expansion_id = sf_e.id
            INNER JOIN expansions cm_e ON cm_p.idExpansion = cm_e.id;
        """
        # Generate the expansion matching table (MKM/Scryfall)
        self.db.query(sql)

        sql = """SELECT distinct cardMarketExpansionId, scryfallExpansionId
        FROM expansions_matching
        WHERE 1
        """
        # Create bidirectional matching dictionary for expansions
        self.matchingext = match2ways(self.db.query(sql))

    def generateCardsMatching(self):
        """
        Generate bidirectional card matching between Oracle IDs and MKM meta card IDs.
        This method identifies cards that have a unique 1:1 relationship between
        Scryfall's Oracle ID and CardMarket's meta card ID system.
        """
        sql = """SELECT 
            sf.oracle_id, 
            MAX(cm.id_meta_card) AS id_meta_card 
            FROM scryfall_products sf 
            LEFT JOIN products cm ON cm.id = sf.card_market_id_id 
            WHERE sf.card_market_id_id IS NOT NULL 
            GROUP BY sf.oracle_id, sf.scryfall_expansion_id
            HAVING COUNT(DISTINCT cm.id_meta_card) = 1"""

        # Create bidirectional matching between Oracle ID and MKM meta card ID
        self.matchingcrd = match2ways(self.db.query(sql))

    def launchMatching(self):
        """
        Launch the automatic matching process for unmatched Scryfall products.
        This method identifies Scryfall cards that have exactly one NULL card_market_id_id
        per oracle_id/expansion pair and attempts to match them with available CardMarket products.
        """
        # Find Scryfall products eligible for matching
        # Only include cards where there's exactly one NULL value per oracle_id/expansion pair
        sql = """SELECT sp.*
                FROM scryfall_products sp
                JOIN (
                    SELECT scryfall_expansion_id, oracle_id
                    FROM scryfall_products
                    GROUP BY scryfall_expansion_id, oracle_id
                    HAVING SUM(CASE WHEN card_market_id_id IS NULL THEN 1 ELSE 0 END) = 1
                ) eligible_pairs ON sp.scryfall_expansion_id = eligible_pairs.scryfall_expansion_id 
                                AND sp.oracle_id = eligible_pairs.oracle_id
                WHERE sp.card_market_id_id IS NULL;"""

        data2match = self.db.query(sql)

        for row in data2match:
            # Skip if oracle_id is not in our card matching dictionary
            if row['oracle_id'] not in self.matchingcrd:
                continue

            # Skip if expansion_id is not in our expansion matching dictionary
            if row['scryfall_expansion_id'] not in self.matchingext:
                continue

            # Get all Scryfall products for this oracle_id and expansion
            sql = f"SELECT * FROM scryfall_products WHERE oracle_id IN ({implode_quoted(',', [row['oracle_id']])}) AND scryfall_expansion_id = '{row['scryfall_expansion_id']}'"
            dataSF = self.db.query(sql)
            
            # Track already used CardMarket IDs and count NULL values
            list_match = ['']  # Start with empty string to avoid SQL errors
            nb_null = nb_not_null = 0
            
            for row2 in dataSF:
                if row2['card_market_id_id'] is None:
                    nb_null += 1
                else:
                    nb_not_null += 1
                    list_match.append(row2['card_market_id_id'])

            # Only proceed if there's exactly one NULL value
            if nb_null == 1:
                # Find available CardMarket products that match criteria and aren't already used
                sql = f"""SELECT * FROM products 
                WHERE id_meta_card IN ({implode_quoted(',', self.matchingcrd[row['oracle_id']])}) 
                AND idExpansion IN ({implode_quoted(',', self.matchingext[row['scryfall_expansion_id']])}) 
                AND id NOT IN ({implode_quoted(',', list_match)})"""
                dataCM = self.db.query(sql)
                
                # If exactly one match found, create the relationship
                if len(dataCM) == 1:
                    sql = f"UPDATE scryfall_products SET card_market_id_id = '{dataCM[0]['id']}' WHERE id = '{row['id']}'"
                    self.db.query(sql)