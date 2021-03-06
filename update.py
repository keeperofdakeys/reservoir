#!/usr/bin/env python3

from data import Database
from bs4 import BeautifulSoup
from datetime import datetime
import pytz
from urllib.request import urlopen
import urllib
from random import randint
from time import sleep
import os

HERE = os.path.dirname(__file__)
DATABASE=os.path.join(HERE, "update.db")

def main():
    db = Database(DATABASE)
    db.update()
    count = 1
    total = len(db.tables)
    for table in db.tables:
        url = db.tables[table]['url']
        timezone = db.tables[table]['timezone']
        try:
          site = BeautifulSoup(urlopen(url))
        except urllib.error.HTTPError:
          print ("error on %s" %(url))
        data = []
        for tr in site('tr'):
            raw_datum = tr.text.strip().split('\n')
            try:
                date = datetime.strptime(raw_datum[0], "%d/%m/%Y %H:%M").replace(
                        tzinfo=pytz.timezone(timezone)
                        )
                value = float(raw_datum[1])
                datum = (date, value)
            except ValueError:
                continue
            data.append(datum)
        db.store_data(data, table)
        sleep(5)
        print ("%d / %d is complete" %(count, total))
        count += 1


if __name__ == "__main__":
    main()
