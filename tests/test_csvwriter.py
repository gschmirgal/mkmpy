import tempfile
import unittest
from pathlib import Path

from mkmpy.csvwriter import CsvWriter, format_value


class FormatValueTest(unittest.TestCase):
    def test_none_is_mysql_null(self):
        self.assertEqual(format_value(None), r"\N")

    def test_bool_is_int(self):
        self.assertEqual(format_value(True), 1)
        self.assertEqual(format_value(False), 0)

    def test_backslash_is_escaped(self):
        self.assertEqual(format_value("a\\b"), "a\\\\b")

    def test_numbers_unchanged(self):
        self.assertEqual(format_value(12), 12)
        self.assertEqual(format_value(0.07), 0.07)


class CsvWriterTest(unittest.TestCase):
    def write(self, columns, rows):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "out.csv"
            with CsvWriter(path, columns) as writer:
                for row in rows:
                    writer.write(row)
            return path.read_text(encoding="utf-8"), writer.count

    def test_columns_order_and_missing_values(self):
        content, count = self.write(("id", "name", "price"), [{"price": 1.5, "id": 3}])
        self.assertEqual(content, "3;\\N;1.5\n")
        self.assertEqual(count, 1)

    def test_quoting(self):
        content, _ = self.write(("name",), [{"name": 'Say "hi"; ok'}, {"name": "Altar's Light"}])
        self.assertEqual(content, '"Say ""hi""; ok"\nAltar\'s Light\n')

    def test_reserved_flag(self):
        content, _ = self.write(("reserved",), [{"reserved": True}, {"reserved": False}])
        self.assertEqual(content, "1\n0\n")


if __name__ == "__main__":
    unittest.main()
