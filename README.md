# Canadian Labour Market Intelligence

How has Alberta's unemployment rate moved relative to Canada, and where does Alberta rank among the provinces in the latest available month?

This project turns the public Labour Force Survey download into a SQLite database, a provincial ranking, and a monthly trend chart. Start with [the example chart](example/unemployment_trends.png) and [provincial snapshot](example/provincial_snapshot.csv).

## Example finding

In October 2026, Alberta's seasonally adjusted unemployment rate was 7.3%, compared with 6.7% for Canada. Alberta was 0.6 percentage points above Canada and down 0.3 percentage points from October 2025. Alberta and Ontario shared the third-highest distinct provincial rate.

## Run on macOS

From the extracted project folder:

```sh
python3 pipeline.py
python3 -m unittest discover -s tests -v
```

The pipeline uses Python 3.10+ and SQLite from the Python standard library. It downloads the full source archive, which was about 58 MB when tested. Use `python3 pipeline.py --source-zip /path/to/14100287-eng.zip` to reuse a downloaded archive. The database and report appear in `outputs/`.

To regenerate the trend chart:

```sh
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python plot_trends.py
open outputs/unemployment_trends.png
```

## Data and methods

Source: [Statistics Canada, Labour Force Survey, table 14-10-0287-01](https://doi.org/10.25318/1410028701-eng). The pipeline keeps monthly seasonally adjusted estimates for all genders and ages 15 and over. It includes Canada and the ten provinces, and loads unemployment, employment, and participation rates from January 2015 onward by default. The run used for the examples included 4,686 observations through October 2026.

The SQLite primary key enforces one row per month, geography, and metric. Source vector IDs and status codes remain in the database. Missing rates remain NULL. The provincial snapshot compares available values in the same month as the latest published Canada observation in the input. Year-over-year change joins to the exact month a year earlier and stays blank when unavailable. Differences are in percentage points and ties share a dense rank.

The national rate comes directly from Statistics Canada. The rates are survey estimates, can be revised, and describe changes without establishing causes. Retain the source ZIP to reproduce a particular vintage.
