#!/usr/bin/env python3
from datetime import datetime, timedelta
from data import Database, to_unixtime
import csv
from io import StringIO

def unixtime_transform(generator):
    for item in generator:
        yield [to_unixtime(item[0]), item[1]]

def get_csv(database, table, date_start=None, date_end=None, granularity=timedelta(hours=1) ):
    if date_end is not None and date_end > datetime.today():
        date_end = datetime.today()
    results = database.load_data_generator(table, date_start, date_end)
    #with open(filename, "w", newline='') as csvfile:
    with StringIO() as csvfile:
        writer = csv.writer(csvfile)
        writer.writerows(unixtime_transform(results))
        return csvfile.getvalue()
