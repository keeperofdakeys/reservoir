#!/usr/bin/env python3

from data import Database
from bs4 import BeautifulSoup
from datetime import datetime
from urllib.request import urlopen

# data_sources = {
#         "gumeracha_weir": "http://www.bom.gov.au/fwo/IDS60248/IDS60248.523755.tbl.shtml",
#         "millbrook_reservoir": "http://www.bom.gov.au/fwo/IDS60248/IDS60248.523763.tbl.shtml"
#     }
# 
# tables = {
#         "gumeracha_weir": "Gumeracha Weir",
#         "millbrook_reservoir": "Millbrook Reservoir"
#     }

def main():
    db = Database("update.db")
    data_sources = db.get_urls()
    for table in db.tables:
        url = data_sources[table]
        site = BeautifulSoup(urlopen(url))
        data = []
        for tr in site('tr'):
            raw_datum = tr.text.strip().split('\n')
            try:
                datum = (table, datetime.strptime(raw_datum[0], "%d/%m/%Y %H:%M"),float(raw_datum[1]))
            except ValueError:
                continue
            if datum[1].minute != 0:
                continue
            data.append(datum)
        db.store_data(data)

if __name__ == "__main__":
    main()
