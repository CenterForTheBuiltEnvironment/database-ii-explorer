import sqlite3
import json
import csv
from flask import g, Flask, render_template, jsonify, request

DATABASE = 'db/ashrae.db'
app = Flask(__name__)

def json2csv(json_in):
    headers = json_in[0].keys()
    r_csv = ','.join(headers) + '\n'  
    for r in json_in:
        r_csv += ','.join([str(v) for v in r.values()]) + '\n'
    return r_csv 

def query_db(query, args=(), one=False):
    cur = get_db().execute(query, args)
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
    db.row_factory = make_dicts
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

@app.route('/buildings', methods = ['GET'])
def buildings():
    fields = request.args.get('field')
    c = get_db().cursor()
    c.execute('select * from building')
    d = []
    while True:
        _d = c.fetchone()
        if _d is not None:
            d.append(c.fetchone())
        else:
            break
    return render_template('buildings.html', buildings=d)

@app.route('/api/query', methods = ['GET'])
def query():
    """
    Query API for the raw data
    """
    fields = request.args.get('fields')
    print fields
    if fields is None:
        return "{}"
    else:
        fields = fields.split(',')
        print fields
        field_range = range(len(fields))
        select = ['t' + str(i) + '.value' for i in field_range]
        tables = ['data t' + str(i) for i in field_range]
        where = ['t' + str(i) + '.fieldid="' + fields[i] + '" ' for i in field_range]
        where += ['t0.respid=t' + str(i) + '.respid ' for i in range(1, len(fields))]
        query = 'select ' + ', '.join(select) + ' from ' + \
                ', '.join(tables) + ' where ' + 'and '.join(where) + ';'

        res = []
        while True:
            d = c.fetchone()
            if d is not None:
                r = {}
                for i in field_range:
                    r[fields[i]] = d[i]
            else:
                break
            res.append(r)
        return json.dumps(res)


@app.route('/data', methods = ['GET'])
def data():
    f = query_db('select * from field')
    return render_template('data.html', fields=f)

@app.route('/api/fields', methods = ['GET'])
def get_fields():
    c = get_db().cursor()
    res = []
    for row in c.execute('select id from field'):
        res.append(row)
    return json.dumps(res)

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)

# query api
# data tables
# render a csv
# proxies
# sass
