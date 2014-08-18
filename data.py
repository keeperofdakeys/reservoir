from datetime import datetime, timedelta
import sqlite3
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
        conn = self.open()
        if date_range_start == None:
            range_start = None
        elif not isinstance(date_range_start, int):
            range_start = to_unixtime(date_range_start)
        else:
            range_start = date_range_start

        if date_range_end == None:
            range_end = None
        elif not isinstance(date_range_end, int):
            range_end = to_unixtime(date_range_end)
        else:
            range_end = date_range_end
        
        query_suffix = ""
        query_parameters = {}
        if range_start is not None and range_end is not None:
            query_suffix = "WHERE date BETWEEN :start AND :end ORDER BY date;"
            query_parameters =  {"start": range_start, "end": range_end}
        elif range_start is not None:
            query_suffix = "WHERE date > :start ORDER BY date;"
            query_parameters = {"start": range_start}
        elif range_end is not None:
            query_suffix = "WHERE date < :end ORDER BY date;"
            query_parameters = {"end": range_end}
        else:
            query_suffix = "ORDER BY date;"
        query_prefixes = ["MIN(date)", "MAX(date)", "date, level"]
        queries = []
        for query_prefix in query_prefixes:
            queries.append( conn.execute("SELECT %s FROM \"%s\" %s"
                % (query_prefix, table, query_suffix),
                query_parameters
            ) )
        # Return min and max dates. Client must use __next__ manually for these.
        yield queries[0].fetchone()
        yield queries[1].fetchone()
        
        while True:
            result_group = queries[2].fetchmany(100)
            if len(result_group) == 0:
                break
            yield result_group

def get_data(database, table, date_start=None, date_end=None):
    timezone = database.tables[table]["timezone"]
    if date_end is None or date_end > datetime.now(pytz.timezone(timezone)):
        date_end = datetime.now(pytz.timezone(timezone))
    results = database.load_data(table, date_start, date_end)
    try:
        min_val = results.__next__()
        max_val = results.__next__()
    except StopIteration:
        return []
    data_period = get_data_period(min_val[0], max_val[0]).total_seconds()
    data = []
    last_time = 0
    for raw_data in results:
        for item in raw_data:
            if item[0] - last_time < data_period:
                continue
            data.append(item)
            last_time = item[0]
    return data

def get_data_period(time_start, time_end):
    time_range = timedelta(seconds=(time_end - time_start))
    data_period = 4 * (time_range / timedelta(weeks=4)) * timedelta(hours=1)
    return data_period
