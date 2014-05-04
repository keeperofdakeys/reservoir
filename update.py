#!/usr/bin/env python3

from data import Database
from bs4 import BeautifulSoup
from datetime import datetime
import pytz
from urllib.request import urlopen

def main():
    db = Database("update.db")
    for table in db.tables:
        url = db.tables[table]['url']
        timezone = db.tables[table]['timezone']
        site = BeautifulSoup(urlopen(url))
        data = []
        for tr in site('tr'):
            raw_datum = tr.text.strip().split('\n')
            try:
                date = datetime.strptime(raw_datum[0], "%d/%m/%Y %H:%M").replace(
                        tzinfo=pytz.timezone(timezone)
                        )
                value = float(raw_datum[1])
                datum = (table, date, value)
            except ValueError:
                continue
            if datum[1].minute != 0:
                continue
            data.append(datum)
        db.store_data(data)

if __name__ == "__main__":
    main()
