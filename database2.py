import sqlite3
import json
import csv
import StringIO
from flask import g, Flask, render_template, jsonify, request, make_response


DATABASE = 'db/ashrae.db'
app = Flask(__name__)


def query_db(query, args=(), one=False):
    """
    this is an easy way to get dicts back from the db,
    though sometimes you have to do it manually
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
    return render_template('buildings.html', buildings=b)

@app.route('/api/export', methods = ['GET'])
def _export():
    fields = request.args.get('fields')
    fmt = request.args.get('format', 'json')
    rv = _query(fields)
    fname = 'download'
    if fmt == 'csv':
        rv = json.loads(rv)
        rv = dict2csv(rv)
    response = make_response(rv)
    response.headers["Content-Disposition"] = "attachment; filename=%s.%s" % (fname, fmt)
    if fmt == 'json':
        response.headers["Content-Type"] = "application/json"
    else:
        response.headers["Content-Type"] = "text/csv"
    return response

def dict2csv(data):
    s = StringIO.StringIO()
    w = csv.DictWriter(s, data[0].keys())
    w.writeheader()
    w.writerows(data)
    csv_str = s.getvalue()
    return csv_str

@app.route('/api/query', methods = ['GET'])
def query():
    """
    Query API for the raw data only
    """
    fields = request.args.get('fields')
    return _query(fields)

def _query(fields):
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
                    try:
                        r[fields[i]] = d[i]
                    except KeyError:
                        pass
            else:
                break
            rv.append(r)
        return json.dumps(rv)

@app.route('/heatmap', methods = ['GET'])
def heatmap():
    f = query_db('select * from field')
    return render_template('heatmap.html', fields=f)

@app.route('/scatter', methods = ['GET'])
def scatter():
    f = query_db('select * from field')
    return render_template('scatter.html', fields=f)

@app.route('/export', methods = ['GET'])
def export():
    f = query_db('select * from field')
    return render_template('export.html', fields=f)

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)

# data tables
# render a csv
# proxies
