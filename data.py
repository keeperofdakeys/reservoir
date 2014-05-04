import sqlite3
from datetime import datetime
import pytz

def to_unixtime(date):
    utcnow = date.astimezone(pytz.utc).replace(tzinfo=None)
    epoch = datetime.utcfromtimestamp(0)
    delta = utcnow - epoch
    return int(delta.total_seconds())

def from_unixtime(time, timezone):
    date = datetime.fromtimestamp(time, pytz.utc)
    return date.astimezone(pytz.timezone(timezone))

class Database():
    def __init__(self, filename):
        self.filename = filename
        conn = self.open()
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute("SELECT count(*) FROM sqlite_master WHERE type='table' and name in (:table1, :table2);",
                    {"table1": "source", "table2": "source_area"})
        result = cur.fetchone()
        if result[0] != 2:
            raise AssertionError()
        cur.execute("""SELECT key, name, url, area, area_name, timezone FROM
                source NATURAL JOIN place NATURAL JOIN source_area""")
        results = cur.fetchall()
        self.tables = dict(
                (r["key"], dict((k, r[k]) for k in r.keys()))
                for r in results
                )
        for table in self.tables:
            cur.execute("SELECT count(*) FROM sqlite_master WHERE type='table' AND name=:table;",
                    {"table": table})
            result = cur.fetchone()
            if result[0] == 0:
                cur.execute("CREATE TABLE \"%s\"(date INTERGER PRIMARY KEY, level REAL);" % (table))
                cur.fetchall()
        cur.close()
        conn.commit()
        conn.close()
    
    def open(self):
        return sqlite3.connect(self.filename, detect_types=sqlite3.PARSE_DECLTYPES)

    def get_urls(self):
        conn = self.open()
        cur = conn.cursor()
        urls = {}
        for table in self.tables:
            cur.execute("SELECT url FROM source WHERE name=:name;",
                    {"name": table})
            urls[table] = cur.fetchone()[0]
        cur.close()
        conn.close()
        return urls

    def store_data(self, data):
        conn = self.open()
        for datum in data:
            if datum[0] not in self.tables or type(datum[1]) is not datetime or type(datum[2]) is not float:
                continue
            date = int(to_unixtime(datum[1]))
            value = datum[2]
            try:
                conn.execute("INSERT INTO \"%s\" VALUES (:date, :value);" % (datum[0]),
                        {"date": date, "value": value})
            except sqlite3.IntegrityError:
                continue
        conn.commit()
        conn.close()

    def load_data(self, table, date_range_start=None, date_range_end=None):
        return [r for r in load_data_generator(table, date_range_start, date_range_end)]

    def load_data_generator(self, table, date_range_start=None, date_range_end=None):
        conn = self.open()
        if date_range_start == None:
            range_start = None
        else:
            range_start = to_unixtime(date_range_start)

        if date_range_end == None:
            range_end = None
        else:
            range_end = to_unixtime(date_range_end)

        if range_start is not None and range_end is not None:
            query = conn.execute("SELECT date, level FROM \"%s\" WHERE date BETWEEN :start AND :end;"
                    % (table), {"start": range_start, "end": range_end})
        elif range_start is not None:
            query = conn.execute("SELECT date, level FROM \"%s\" WHERE date > :start;"
                    % (table), {"start": range_start})
        elif range_end is not None:
            query = conn.execute("SELECT date, level FROM \"%s\" WHERE date < :end;"
                    % (table), {"end": range_end})
        else:
            query = conn.execute("SELECT date, level FROM \"%s\";" % (table))
       
        timezone = self.tables[table]["timezone"]
        while True:
            result_group = query.fetchmany(20)
            if len(result_group) == 0:
                break
            for result in result_group:
                yield [from_unixtime(result[0], timezone),result[1]]

