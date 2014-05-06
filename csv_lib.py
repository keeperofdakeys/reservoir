#!/usr/bin/env python3
from datetime import datetime, timedelta
import pytz
from data import Database, to_unixtime
import csv
from io import StringIO


def unixtime_transform(generator):
    for item in generator:
        yield [to_unixtime(item[0]), item[1]]

def reduce_data(generator, filter_func):
    for item in generator:
        if filter_func(item):
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
            filter_func = lambda x: x.hour == 0
        elif time_range > timedelta(weeks=13):
            filter_func = lambda x: x.hour == 0 and x.day % 3 == 0
        elif time_range > timedelta(weeks=26):
            filter_func = lambda x: x.hour == 0 and x.day % 6 == 0
        elif time_range > timedelta(weeks=39):
            filter_func = lambda x: x.hour == 0 and x.day % 9 == 0
        elif time_range > timedelta(weeks=52):
            filter_func = lambda x: x.hour == 0 and x.day % 12 == 0
        else:
            filter_func = lambda x: x.hour == 0 and x.day == 0
    else:
        filter_func = lambda x: True
    with StringIO() as csvfile:
        writer = csv.writer(csvfile)
        writer.writerows(
                reduce_data(unixtime_transform(results), filter_func)
                )
        return csvfile.getvalue()
