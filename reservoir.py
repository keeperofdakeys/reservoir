#!/usr/bin/env python3
from datetime import datetime, timedelta
from data import Database, from_unixtime
from flask import Flask, abort, json
from werkzeug.contrib.cache import FileSystemCache
from jinja2 import Environment, PackageLoader
from csv_lib import get_csv, get_dict
import os

app = Flask(__name__)

CACHE_TIMEOUT = 60 * 60
HERE = os.path.dirname(__file__)
CACHE_DIR=os.path.join(HERE, "cache")
DATABASE=os.path.join(HERE, "update.db")
TEMPLATES=os.path.join(HERE, "templates")
cache = FileSystemCache(CACHE_DIR, threshold=100, default_timeout=CACHE_TIMEOUT, mode=600)

env = Environment(loader=PackageLoader(__name__, "templates"))

@app.route("/")
def home():
    db = Database(DATABASE)
    template = env.get_template('graph.html')
    return template.render(title="Reservoir Levels",
            #tables=[db.tables[table] for table in db.tablesl],
            tables=db.tables, areas=db.areas, states=db.states,
            static_dir="static")

@app.route("/data/<tables>/start/<int:end>/", defaults={"start": None})
@app.route("/data/<tables>/<int:start>/end/", defaults={"end": None})
@app.route("/data/<tables>/start/end/", defaults={"start": None, "end": None})
@app.route("/data/<tables>/<int:start>/<int:end>/")
def data(tables, start, end):
    db = Database(DATABASE)
    table_list = tables.split("+")
    table_set = set()
    table_data = dict()
    for table in table_list:
        if table in db.tables:
            table_set.add(table)
            data = get_data(db, table, start, end)
            table_data[table] = data

    # We don't fail if at least one table is found. While the client should
    # never request an unknown table, it will not error if it doesn't receive
    # a requested table, and will just draw those given.
    if len(table_set) == 0:
        abort(404)
    
    return json.jsonify(table_data)

def get_data(db, table, start, end):
    name = "%s_%s" % (start, end)
    cached = cache.get(name)
    if cached is not None:
        return cached

    timezone = db.tables[table]["timezone"]
    if start is None:
        start_date = None
    else:
        start_date = from_unixtime(start, timezone)
    if end is None:
        end_date = None
    else:
        end_date = from_unixtime(end, timezone)

    value = get_dict(db, table, start_date, end_date)
    cache.set(name, value)

    return value

if __name__ == '__main__':
    app.run(debug=True)#, host="0.0.0.0")

