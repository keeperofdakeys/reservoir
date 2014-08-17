#!/usr/bin/env python3
from datetime import datetime, timedelta
import pytz
from data import Database, to_unixtime, get_data
import csv
from io import StringIO

def get_csv(database, table, date_start=None, date_end=None):
    timezone = database.tables[table]["timezone"]
    data = get_data(database, table, date_start, date_end)
    with StringIO() as csvfile:
        writer = csv.writer(csvfile)
        writer.writerows(data)
        return csvfile.getvalue()
