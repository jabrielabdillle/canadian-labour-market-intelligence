"""Build a monthly labour-market database from Statistics Canada table 14-10-0287-01."""
import argparse
import csv
from datetime import date
import io
from pathlib import Path
import shutil
import sqlite3
from tempfile import TemporaryDirectory
from urllib.request import urlopen
from zipfile import ZipFile

URL = "https://www150.statcan.gc.ca/n1/tbl/csv/14100287-eng.zip"
ROOT = Path(__file__).resolve().parent
GEOS = {"Canada", "Newfoundland and Labrador", "Prince Edward Island",
        "Nova Scotia", "New Brunswick", "Quebec", "Ontario", "Manitoba",
        "Saskatchewan", "Alberta", "British Columbia"}
METRICS = {"Unemployment rate", "Employment rate", "Participation rate"}


def read_rates(stream, start):
    rows = []
    for row in csv.DictReader(stream):
        if (row["REF_DATE"] < start or row["GEO"] not in GEOS
                or row["Labour force characteristics"] not in METRICS
                or row["Gender"] != "Total - Gender"
                or row["Age group"] != "15 years and over"
                or row["Statistics"] != "Estimate"
                or row["Data type"] != "Seasonally adjusted"):
            continue
        month = date.fromisoformat(row["REF_DATE"] + "-01").isoformat()
        value = float(row["VALUE"]) if row["VALUE"] else None
        if value is not None and not 0 <= value <= 100:
            raise ValueError(f"Rate outside 0–100 for {month}, {row['GEO']}")
        rows.append((month, row["GEO"], row["Labour force characteristics"],
                     value, row["STATUS"], row["VECTOR"]))
    if not rows:
        raise ValueError("No matching observations for the requested start month.")
    return rows


def build(archive, start, output):
    with ZipFile(archive) as source, source.open("14100287.csv") as raw:
        rows = read_rates(io.TextIOWrapper(raw, encoding="utf-8-sig"), start)
    output.mkdir(parents=True, exist_ok=True)
    with TemporaryDirectory(dir=output) as staging:
        stage = Path(staging)
        with sqlite3.connect(stage / "labour.sqlite") as db:
            db.executescript((ROOT / "sql/schema.sql").read_text())
            db.executemany("INSERT INTO rates VALUES (?, ?, ?, ?, ?, ?)", rows)
            result = db.execute((ROOT / "sql/provincial_snapshot.sql").read_text())
            with (stage / "provincial_snapshot.csv").open("w", newline="") as report:
                writer = csv.writer(report)
                writer.writerow([column[0] for column in result.description])
                writer.writerows(result)
        for artifact in stage.iterdir():
            artifact.replace(output / artifact.name)
    print(f"Loaded {len(rows):,} observations through {max(row[0] for row in rows)[:7]}.")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-zip", type=Path, help="Reuse a downloaded source archive")
    parser.add_argument("--start", default="2015-01", help="First month to include, YYYY-MM")
    parser.add_argument("--output", type=Path, default=ROOT / "outputs")
    args = parser.parse_args()
    try:
        if date.fromisoformat(args.start + "-01").strftime("%Y-%m") != args.start:
            raise ValueError
    except ValueError:
        parser.error("--start must be YYYY-MM")
    if args.source_zip:
        build(args.source_zip, args.start, args.output)
        return
    with TemporaryDirectory() as temp:
        archive = Path(temp) / "source.zip"
        with urlopen(URL, timeout=60) as response, archive.open("wb") as destination:
            shutil.copyfileobj(response, destination)
        build(archive, args.start, args.output)


if __name__ == "__main__":
    main()
