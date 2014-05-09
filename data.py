import sqlite3
from datetime import datetime, timedelta
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
        cur.execute("SELECT count(*) FROM sqlite_master WHERE type='table' and name in (:table1, :table2, :table3);",
                    {"table1": "source", "table2": "place", "table3": "state"})
        result = cur.fetchone()
        if result[0] != 3:
            raise AssertionError()
        cur.execute("""SELECT key, name, url, area, area_name, timezone, state, state_name FROM
                source NATURAL JOIN place NATURAL JOIN state;""")
        results = cur.fetchall()
        self.tables = dict(
                (r["key"], dict((k, r[k]) for k in r.keys()))
                for r in results
                )
        cur.execute("SELECT area, area_name, state, state_name FROM state NATURAL JOIN place;")
        results = cur.fetchall()
        self.areas = {}
        self.states = {}
        for r in results:
            area = r["area"]
            state = r["state"]
            if state not in self.states:
                self.states[state] = {"areas": {}}
            item = dict((k, r[k]) for k in r.keys())
            self.areas[area] = item
            self.areas[area]["keys"] = []
            self.states[state]["state"] = r["state"]
            self.states[state]["state_name"] = r["state_name"]
            self.states[state]["areas"][area] = item
            self.states[state]["areas"][area]["keys"] = []
        for k in self.tables:
            t = self.tables[k]
            self.areas[t["area"]]["keys"].append(t["key"])

            
        conn.close()

    def update(self):
        conn = self.open(isolation_level="immediate")
        cur = conn.cursor()
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

    
    def open(self, isolation_level="DEFFERED"):
        return sqlite3.connect(self.filename, detect_types=sqlite3.PARSE_DECLTYPES,
                timeout=10, isolation_level=isolation_level)

    def store_data(self, data, table):
        if table not in self.tables:
            return
        conn = self.open("IMMEDIATE")
        cur = conn.cursor()
        cur.execute("SELECT MAX(date) FROM \"%s\";" % (table))
        result = cur.fetchone()
        if result[0] is None:
            last_time = 0
        else:
            last_time = result[0]
        cur.execute
        hour = timedelta(hours=1).total_seconds()
        for datum in data:
            if type(datum[0]) is not datetime or type(datum[1]) is not float:
                continue
            date = int(to_unixtime(datum[0]))
            value = datum[1]
            
            if date - last_time < hour:
                continue
            last_time = date

            try:
                conn.execute("INSERT INTO \"%s\" VALUES (:date, :value);" % (table),
                        {"date": date, "value": value})
            except sqlite3.IntegrityError:
                continue
        cur.close()
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
            query = conn.execute("""SELECT date, level FROM \"%s\" WHERE date
                    BETWEEN :start AND :end ORDER BY date;"""
                    % (table), {"start": range_start, "end": range_end})
        elif range_start is not None:
            query = conn.execute("SELECT date, level FROM \"%s\" WHERE date > :start ORDER BY date;"
                    % (table), {"start": range_start})
        elif range_end is not None:
            query = conn.execute("SELECT date, level FROM \"%s\" WHERE date < :end ORDER BY date;"
                    % (table), {"end": range_end})
        else:
            query = conn.execute("SELECT date, level FROM \"%s\" ORDER BY date;" % (table))
       
        timezone = self.tables[table]["timezone"]
        while True:
            result_group = query.fetchmany(20)
            if len(result_group) == 0:
                break
            for result in result_group:
                yield [from_unixtime(result[0], timezone),result[1]]

