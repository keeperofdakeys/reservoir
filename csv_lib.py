#!/usr/bin/env python3
from datetime import datetime, timedelta
import pytz
from data import Database, to_unixtime
import csv
from io import StringIO


def unixtime_transform(generator):
    for item in generator:
        yield [to_unixtime(item[0]), item[1]]

def get_data_period(date_start, date_end):
    time_range = date_end - date_start
    data_period = 4 * (time_range / timedelta(weeks=4)) * timedelta(hours=1)

    return data_period

def reduce_data(data, date_start=None, date_end=None):
    last_time = 0
    try:
        item = data.__next__()
    except StopIteration:
        raise StopIteration()
    last_time = item[0]
    date_start = datetime.fromtimestamp(item[0], pytz.utc)
    yield item

    if date_end is None:
        date_end = datetime.now(pytz.utc)
    data_period = get_data_period(date_start, date_end).total_seconds()
    for item in data:
        date = item[0]
        if date - last_time < data_period:
            continue
        last_time = date
        yield item

def get_csv(database, table, date_start=None, date_end=None):
    timezone = database.tables[table]["timezone"]
    if date_end is None or date_end > datetime.now(pytz.timezone(timezone)):
        date_end = datetime.now(pytz.timezone(timezone))
    results = database.load_data_generator(table, date_start, date_end)
    #with open(filename, "w", newline='') as csvfile:
    
    with StringIO() as csvfile:
        writer = csv.writer(csvfile)
        writer.writerows(
                reduce_data(unixtime_transform(results), date_start, date_end)
                )
        return csvfile.getvalue()
