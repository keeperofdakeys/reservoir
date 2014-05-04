#!/usr/bin/env python3
from datetime import datetime, timedelta
from data import Database, from_unixtime
from flask import Flask, abort
from werkzeug.contrib.cache import FileSystemCache
from jinja2 import Environment, PackageLoader
from csv_lib import get_csv

app = Flask(__name__)

# Sed timeout for 24 hours, since data doesn't change much.
CACHE_TIMEOUT = 24 * 60 * 60
cache = FileSystemCache("cache", threshold=100, default_timeout=CACHE_TIMEOUT, mode=600)

env = Environment(loader=PackageLoader(__name__, 'templates'))

@app.route("/")
def home():
    db = Database("update.db")
    template = env.get_template('graph.html')
    return template.render(title="Reservoir Levels",
            tables=[db.tables[table] for table in db.tables],
            static_dir="static")

@app.route("/data/<table>/start/<int:end>/", defaults={"start": None})
@app.route("/data/<table>/<int:start>/end/", defaults={"end": None})
@app.route("/data/<table>/start/end/", defaults={"start": None, "end": None})
@app.route("/data/<table>/<int:start>/<int:end>/")
def data(table, start, end):
    db = Database("update.db")
    if table not in db.tables:
        abort(404)

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

    value = get_csv(db, table, start_date, end_date)
    cache.set(name, value)

    return value

if __name__ == '__main__':
    app.run(debug=True)

