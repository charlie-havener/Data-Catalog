from flask import Flask, render_template, request
from collections import defaultdict
import json
import time

import utils.database_functions as db

# >flask --app server run --debug --port 3000
app = Flask(__name__, static_url_path='/static')
print('started')

@app.route('/')
def index():
    return render_template('home/index.html')


@app.route('/view/<int:db_id>/<int:ob_id>')
def view(db_id, ob_id):
    (conn, c) = db.get_cursor('database_objects.db')

    # Get the object information
    db.query_object_info(c, db_id, ob_id)
    obj = c.fetchone()

    # Get the column information
    db.query_columns_info(c, db_id, ob_id)
    cols = c.fetchall()

    # Get the index information
    db.query_indexes_info(c, db_id, ob_id)
    idxs = c.fetchall()

    conn.close()
    return render_template('view/index.html', obj=obj, cols=cols, idxs=idxs)


@app.route('/edit/<int:db_id>/<int:ob_id>', methods=['GET', 'PUT'])
def edit_object_desc(db_id, ob_id):
    (conn, c) = db.get_cursor('database_objects.db')

    if request.method == 'PUT':
        desc = request.form.get('updated-desc')
        desc = db.sanatize(desc)

        db.query_desc_upsert(c, db_id, ob_id, desc)
        conn.commit()
        conn.close()

        request.method = 'GET'
        return edit_object_desc(db_id, ob_id)

    # default GET
    db.query_object_info(c, db_id, ob_id)
    obj = c.fetchone()

    conn.close()
    return render_template('view/_partials/show_object.html', obj=obj)


@app.route('/edit/<int:db_id>/<int:ob_id>/<int:col_id>', methods=['GET', 'PUT'])
def edit_column_desc(db_id, ob_id, col_id):
    (conn, c) = db.get_cursor('database_objects.db')

    if request.method == 'PUT':
        desc = request.form.get('updated-desc')
        desc = db.sanatize(desc)

        db.query_col_desc_upsert(c, db_id, ob_id, col_id, desc)
        conn.commit()
        conn.close()

        request.method = 'GET'
        return edit_column_desc(db_id, ob_id, col_id)

    # default GET
    db.query_column_info(c, db_id, ob_id, col_id)
    col = c.fetchone()

    conn.close()
    return render_template('view/_partials/show_column_row.html', col=col)


@app.route('/search', methods=['POST'])
def search_tasks():
    search_string = request.form.get('search')
    filter = request.form.get('filter')
    (conn, c) = db.get_cursor('database_objects.db')
    db.query_search(c, search_string, filter)
    obj = c.fetchmany(50)
    conn.close()
    return render_template('home/_partials/search_results.html', obj=obj)


@app.route('/test')
def test():
    roots = [5]  # TOOD: make whatever the db item is
    depth = 6

    # need a base (root element with no parent)
    data = [{'name': roots[0], 'parent': ''}]

    while depth > 0:
        (conn, c) = db.get_cursor('database_objects.db')
        db.query_dependencies_upstream(c, roots)
        t = c.fetchall()
        c.close()
        roots.clear()
        for (parent, child) in t:
            data.append({'name': child, 'parent': parent})
            roots.append(child)
        if len(roots) == 0:
            break
        depth -= 1
    return render_template('test.html', data=data)
