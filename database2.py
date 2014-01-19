import sqlite3
import json
import csv
from flask import g, Flask, render_template, jsonify, request

DATABASE = 'db/ashrae.db'
app = Flask(__name__)


def query_db(query, args=(), one=False):
    """
    this is an easy way to get dicts back from the db,
    though sometimes you have to do it manually like
    in data()
    """
    db = get_db()
    db.row_factory = make_dicts
    cur = db.execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv

def make_dicts(cursor, row):
    return dict((cursor.description[idx][0], value)
                for idx, value in enumerate(row))

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

@app.route('/buildings', methods = ['GET'])
def buildings():
    b = query_db('select * from building')
    return render_template('buildings.html', buildings=d)

@app.route('/api/query', methods = ['GET'])
def query():
    """
    Query API for the raw data
    """
    fields = request.args.get('fields')
    if fields is None:
        return "{}"
    else:
        fields = fields.split(',')
        field_range = range(len(fields))
        select = ['t' + str(i) + '.value' for i in field_range]
        tables = ['data t' + str(i) for i in field_range]
        where = ['t' + str(i) + '.fieldid="' + fields[i] + '" ' for i in field_range]
        where += ['t0.respid=t' + str(i) + '.respid ' for i in range(1, len(fields))]
        select_str = ', '.join(select)
        tables_str = ', '.join(tables)
        where_str = 'and '.join(where)
 
        # not secure
        query = 'select ' + select_str + ' from ' + \
                tables_str + ' where ' + where_str + ';'

        c = get_db().cursor()
        c.execute(query)
        rv = []
        while True:
            d = c.fetchone()
            if d is not None:
                r = {}
                for i in field_range:
                    r[fields[i]] = d[i]
            else:
                break
            rv.append(r)
        return json.dumps(rv)


@app.route('/data', methods = ['GET'])
def data():
    f = query_db('select * from field')
    return render_template('data.html', fields=f)

@app.route('/api/fields', methods = ['GET'])
def get_fields():
    rv = query_db('select * from field')
    return json.dumps(rv)

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)

# data tables
# render a csv
# proxies
