#!/usr/bin/env python3
from datetime import datetime, timedelta
from data import Database
from flask import Flask, abort
from werkzeug.contrib.cache import FileSystemCache
from jinja2 import Environment, PackageLoader
from csv_lib import get_csv

app = Flask(__name__)

# Sed timeout for 24 hours, since data doesn't change much.
CACHE_TIMEOUT = 24 * 60 * 60
cache = FileSystemCache("cache", threshold=100, default_timeout=CACHE_TIMEOUT, mode=600)

env = Environment(loader=PackageLoader(__name__, 'templates'))

@app.route('/')
def home():
    db = Database("update.db")
    template = env.get_template('graph.html')
    return template.render(title="Reservoir Levels",
            tables=[db.tables[table] for table in db.tables],
            static_dir="static")

@app.route('/data/<table>/<data_type>/<start>/')
def data(table, data_type, start):
    print (table, data_type, start)
    db = Database("update.db")
    if table not in db.tables:
        abort(404)

    name = "%s_%s" % (data_type, start)
    cached = cache.get(name)
    if cached is None:
        value = get_csv(db, table)
        cache.set(name, value)
    else:
        value = cached
    return value

if __name__ == '__main__':
    app.run(debug=True)

