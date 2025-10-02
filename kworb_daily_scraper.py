"""
kworb_daily_scraper.py
Scrapes Kworb Spotify Global Daily Top 200 for one year,
saves raw daily data to kworb_daily_YEAR.csv

Usage:
    python kworb_daily_scraper.py 2020
"""

import sys
import pandas as pd
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from time import sleep

BASE_URL = "https://kworb.net/spotify/daily/{date}.html"
HEADERS = {"User-Agent": "Mozilla/5.0 (friendly-scraper/1.0)"}

def daterange(year):
    start = datetime(year, 1, 1)
    end = datetime(year, 12, 31)
    delta = timedelta(days=1)
    while start <= end:
        yield start.strftime("%Y-%m-%d")
        start += delta

def scrape_day(date_str):
    url = BASE_URL.format(date=date_str)
    r = requests.get(url, headers=HEADERS, timeout=20)
    if r.status_code != 200:
        return []
    soup = BeautifulSoup(r.text, "html.parser")
    table = soup.find("table", {"class": "sortable"})
    if not table:
        return []
    out = []
    for tr in table.find_all("tr")[1:]:
        tds = tr.find_all("td")
        if len(tds) < 5:
            continue
        artist = tds[2].text.strip()
        title = tds[1].text.strip()
        try:
            streams = int(tds[3].text.replace(",", ""))
        except:
            continue
        out.append({"date": date_str, "artist": artist, "title": title, "streams": streams})
    return out

def main(year):
    rows = []
    for d in daterange(year):
        items = scrape_day(d)
        if items:
            rows.extend(items)
        sleep(0.3)
    if not rows:
        print(f"No data scraped for {year}")
        return
    df = pd.DataFrame(rows)
    out = f"kworb_daily_{year}.csv"
    df.to_csv(out, index=False)
    print(f"✅ Saved {out} with {df.shape[0]} rows")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python kworb_daily_scraper.py YEAR")
    else:
        year = int(sys.argv[1])
        main(year)
