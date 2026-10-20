import configparser
import datetime
import unittest

from mkmpy.datasets import CARDMARKET_DATASETS, SCRYFALL_DATASETS
from mkmpy.lib import convert_to_datetime, get_boolean, yesterday
from mkmpy.scryfall import get_nested_value


class ConvertToDatetimeTest(unittest.TestCase):
    def test_cardmarket_format_ignores_timezone(self):
        self.assertEqual(convert_to_datetime("2026-10-20T02:44:37+0200"), datetime.datetime(2026, 10, 20, 2, 44, 37))

    def test_date_only(self):
        self.assertEqual(convert_to_datetime("2025-06-01"), datetime.datetime(2025, 6, 1))

    def test_invalid_raises(self):
        with self.assertRaises(ValueError):
            convert_to_datetime("pas une date")

    def test_yesterday(self):
        self.assertEqual(yesterday(datetime.datetime(2026, 3, 1, 2)), datetime.datetime(2026, 2, 28, 2))


class GetBooleanTest(unittest.TestCase):
    def value(self, text):
        config = configparser.ConfigParser()
        config.read_string(text)
        return get_boolean(config, "Database", "enabled", default=True)

    def test_missing_or_empty_uses_default(self):
        self.assertTrue(self.value(""))
        self.assertTrue(self.value("[Database]\nhost = x\n"))
        self.assertTrue(self.value("[Database]\nenabled =\n"))

    def test_explicit_values(self):
        self.assertFalse(self.value("[Database]\nenabled = false\n"))
        self.assertFalse(self.value("[Database]\nenabled = no\n"))
        self.assertTrue(self.value("[Database]\nenabled = true\n"))


class GetNestedValueTest(unittest.TestCase):
    card = {"name": "Delver", "image_uris": {"png": "x.png"}, "card_faces": [{"name": "A"}, {"name": "B"}]}

    def test_paths(self):
        self.assertEqual(get_nested_value(self.card, "name"), "Delver")
        self.assertEqual(get_nested_value(self.card, "image_uris.png"), "x.png")
        self.assertEqual(get_nested_value(self.card, "card_faces.1.name"), "B")

    def test_missing_returns_none(self):
        self.assertIsNone(get_nested_value(self.card, "image_uris.normal"))
        self.assertIsNone(get_nested_value(self.card, "card_faces.2.name"))
        self.assertIsNone(get_nested_value(self.card, "name.x"))


class DatasetsTest(unittest.TestCase):
    def test_filenames(self):
        names = [d.filename for d in CARDMARKET_DATASETS + SCRYFALL_DATASETS]
        self.assertEqual(names, ["expansions_file.csv", "products_file.csv", "prices_file.csv",
                                 "scryfall_expansions_file.csv", "scryfall_products_file.csv"])


if __name__ == "__main__":
    unittest.main()
