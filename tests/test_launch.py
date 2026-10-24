import unittest

from launch import create_expansions_csv, create_missing_expansions, rename_unknown_expansions


class FakeCardmarket:
    def __init__(self, error=None):
        self.error = error
        self.called = False

    def create_expansions_csv(self):
        self.called = True
        if self.error:
            raise self.error
        return {1: "Alpha"}


class CreateExpansionsCsvTest(unittest.TestCase):
    def test_scraping_ok(self):
        cardmarket = FakeCardmarket()
        self.assertEqual(create_expansions_csv(cardmarket, scrape=True), {1: "Alpha"})

    def test_scraping_fails_does_not_block(self):
        cardmarket = FakeCardmarket(RuntimeError("Cloudflare"))
        with self.assertLogs("mkmpy", level="WARNING"):
            self.assertIsNone(create_expansions_csv(cardmarket, scrape=True))

    def test_scraping_disabled(self):
        cardmarket = FakeCardmarket()
        self.assertIsNone(create_expansions_csv(cardmarket, scrape=False))
        self.assertFalse(cardmarket.called)


class FakeDb:
    def __init__(self, existing_ids=(), rows=()):
        self.existing_ids = existing_ids
        self.rows = rows
        self.inserted = []
        self.updated = []

    def query(self, query, params=None):
        if query.startswith("SELECT id, name"):
            return list(self.rows)
        if query.startswith("SELECT"):
            return [{"id": i} for i in self.existing_ids]
        if query.startswith("UPDATE"):
            self.updated.append(params)
        else:
            self.inserted.append(params)


class CreateMissingExpansionsTest(unittest.TestCase):
    def test_creates_only_missing(self):
        db = FakeDb({1, 2})
        with self.assertLogs("mkmpy", level="WARNING"):
            create_missing_expansions(db, {1, 2, 5, 3})
        self.assertEqual(db.inserted, [(3, "Unknown expansion 3"), (5, "Unknown expansion 5")])

    def test_nothing_missing_is_silent(self):
        db = FakeDb({1, 2})
        with self.assertNoLogs("mkmpy", level="WARNING"):
            create_missing_expansions(db, {1, 2})
        self.assertEqual(db.inserted, [])


class RenameUnknownExpansionsTest(unittest.TestCase):
    def test_renames_only_placeholders(self):
        # Le LIKE peut ramener une extension déjà renommée à la main au nom proche : elle est ignorée
        db = FakeDb(rows=[
            {"id": 3, "name": "Unknown expansion 3"},
            {"id": 4, "name": "Unknown expansion 4 (Promo)"},
            {"id": 7, "name": "Unknown expansion 7"},
        ])
        rename_unknown_expansions(db, {3: "Beta", 4: "Promos", 5: "Gamma"})
        self.assertEqual(db.updated, [("Beta", 3, "Unknown expansion 3")])


if __name__ == "__main__":
    unittest.main()
