from flask import Flask, render_template, request
import time

import utils.database_functions as db

# >flask --app server run --debug --port 3000
app = Flask(__name__, static_url_path='/static')


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


# TODO: change to edit description information
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
    time.sleep(1)
    search_string = request.form.get('search')
    filter = request.form.get('filter')
    (conn, c) = db.get_cursor('database_objects.db')
    db.query_search(c, search_string, filter)
    obj = c.fetchmany(50)
    conn.close()
    return render_template('home/_partials/search_results.html', obj=obj)
