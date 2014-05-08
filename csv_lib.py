#!/usr/bin/env python3
from datetime import datetime, timedelta
import pytz
from data import Database, to_unixtime
import csv
from io import StringIO


def unixtime_transform(generator):
    for item in generator:
        yield [to_unixtime(item[0]), item[1]]

def reduce_data(data, data_period=None):
    if data_period is None:
        return data
    last_time = 0
    data_period = data_period.total_seconds()
    for item in data:
        date = item[0]
        if date - last_time < data_period:
            continue
        last_time = date
        yield item

def get_csv(database, table, date_start=None, date_end=None):
    timezone = database.tables[table]["timezone"]
    if date_end is not None and date_end > datetime.now(pytz.timezone(timezone)):
        date_end = datetime.now(pytz.timezone(timezone))
    results = database.load_data_generator(table, date_start, date_end)
    #with open(filename, "w", newline='') as csvfile:
    
    if date_start is not None and date_end is not None:
        time_range = date_end - date_start
        if time_range > timedelta(days=30):
            data_period = timedelta(hours=1)
        elif time_range > timedelta(weeks=13):
            data_period = timedelta(days=1)
        elif time_range > timedelta(weeks=26):
            data_period = timedelta(days=2)
        elif time_range > timedelta(weeks=39):
            data_period = timedelta(days=3)
        elif time_range > timedelta(weeks=52):
            data_period = timedelta(days=4)
        else:
            data_period = timedelta(days=12)
    else:
        data_period = timedelta(seconds=1)
    with StringIO() as csvfile:
        writer = csv.writer(csvfile)
        writer.writerows(
                reduce_data(unixtime_transform(results), data_period)
                )
        return csvfile.getvalue()
