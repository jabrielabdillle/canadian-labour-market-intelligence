import io
import sqlite3
import unittest

from pipeline import ROOT, read_rates

HEADER = "REF_DATE,GEO,Labour force characteristics,Gender,Age group,Statistics,Data type,VALUE,STATUS,VECTOR\n"


class LabourMarketTests(unittest.TestCase):
    def test_filter_preserves_missing_rate_and_source(self):
        prefix = "2025-01,Alberta,Unemployment rate,Total - Gender,15 years and over,Estimate,"
        stream = io.StringIO(HEADER + prefix + "Seasonally adjusted,,x,v1\n"
                             + prefix + "Unadjusted,7.0,,v2\n")
        self.assertEqual(read_rates(stream, "2025-01"),
                         [("2025-01-01", "Alberta", "Unemployment rate", None, "x", "v1")])

    def test_snapshot_uses_exact_year_ago_and_common_month(self):
        with sqlite3.connect(":memory:") as db:
            db.executescript((ROOT / "sql/schema.sql").read_text())
            db.executemany("INSERT INTO rates VALUES (?, ?, 'Unemployment rate', ?, '', '')", [
                ("2025-09-01", "Canada", 7), ("2025-09-01", "Alberta", 8),
                ("2024-09-01", "Alberta", 6), ("2025-08-01", "Alberta", 9),
            ])
            row = db.execute((ROOT / "sql/provincial_snapshot.sql").read_text()).fetchone()
            self.assertEqual(row, ("2025-09-01", "Alberta", 8, 2, 1, 1))
