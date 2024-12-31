from flask import Flask, render_template, request
import utils.database_functions as db

# >flask --app server run --debug --port 3000
app = Flask(__name__, static_url_path='/static')


@app.route('/')
def index():
    return render_template('home/index.html')


@app.route('/view/object/<int:object_id>', methods=['GET'])
def view(object_id):
    (conn, c) = db.get_cursor('data_catalog.db')

    # Get the object information
    db.query_object_info(c, object_id)
    obj = c.fetchone()

    # Get the column information
    db.query_columns_info(c, object_id)
    cols = c.fetchall()

    # Get the index information
    db.query_indexes_info(c, object_id)
    idxs = c.fetchall()

    # Dependency information
    up_roots = [object_id]
    down_roots = [object_id]
    depth = 6

    # need a base (root element with no parent)
    up_data = [{'name': obj[1], 'parent': '', 'id': obj[0]}]
    down_data = [{'name': obj[1], 'parent': '', 'id': obj[0]}]

    tmp_depth = depth
    while tmp_depth > 0:
        db.query_dependencies_upstream(c, up_roots)
        up = c.fetchall()
        up_roots.clear()
        for (parent_id, parent_name, child_id, child_name) in up:
            up_data.append({'name': child_name, 'parent': parent_name, 'id': child_id})
            up_roots.append(child_id)
        if len(up_roots) == 0:
            break
        tmp_depth -= 1

    tmp_depth = depth
    while tmp_depth > 0:
        db.query_dependencies_downstream(c, down_roots)
        down = c.fetchall()
        down_roots.clear()
        for (parent_id, parent_name, child_id, child_name) in down:
            down_data.append({'name': parent_name, 'parent': child_name, 'id': parent_id})
            down_roots.append(parent_id)
        if len(down_roots) == 0:
            break
        tmp_depth -= 1

    conn.close()
    return render_template('view/index.html', obj=obj, cols=cols, idxs=idxs, up_data=up_data, down_data=down_data)


@app.route('/edit/object/<int:object_id>', methods=['GET', 'PUT'])
def edit_object_desc(object_id):
    (conn, c) = db.get_cursor('data_catalog.db')

    if request.method == 'PUT':
        desc = request.form.get('updated-desc')
        desc = db.sanatize(desc)

        db.query_object_desc_upsert(c, object_id, desc)
        conn.commit()
        conn.close()

        request.method = 'GET'
        return edit_object_desc(object_id)

    # default GET
    db.query_object_info(c, object_id)
    obj = c.fetchone()

    conn.close()
    return render_template('view/_partials/show_object.html', obj=obj)


@app.route('/edit/column/<int:column_id>', methods=['GET', 'PUT'])
def edit_column_desc(column_id):
    (conn, c) = db.get_cursor('data_catalog.db')

    if request.method == 'PUT':
        desc = request.form.get('updated-desc')
        desc = db.sanatize(desc)

        db.query_col_desc_upsert(c, column_id, desc)
        conn.commit()
        conn.close()

        request.method = 'GET'
        return edit_column_desc(column_id)

    # default GET
    db.query_column_info(c, column_id)
    col = c.fetchone()

    conn.close()
    return render_template('view/_partials/show_column_row.html', col=col)


@app.route('/search', methods=['POST'])
def search_tasks():
    search_string = request.form.get('search')
    filter = request.form.get('filter')
    (conn, c) = db.get_cursor('data_catalog.db')
    db.query_search(c, search_string, filter)
    obj = c.fetchmany(50)
    conn.close()
    return render_template('home/_partials/search_results.html', obj=obj)


@app.route('/search_add', methods=['POST'])
def search_tasks_add():
    search_string = request.form.get('search')
    filter = request.form.get('filter')
    (conn, c) = db.get_cursor('data_catalog.db')
    db.query_search(c, search_string, filter)
    obj = c.fetchmany(50)
    conn.close()
    return render_template('objects/_partials/search_results.html', obj=obj)


@app.route('/add_dependency/<int:object_id>', methods=['GET'])
def add_dependency(object_id):
    print(object_id)
    (conn, c) = db.get_cursor('data_catalog.db')
    db.query_object_info(c, object_id)
    obj = c.fetchone()
    conn.close()
    return render_template('objects/_partials/search_add.html', obj=obj)


@app.route('/objects/new_object', methods=['GET'])
def new_object():
    (conn, c) = db.get_cursor('data_catalog.db')
    db.query_user_object_types(c)
    types = c.fetchall()
    conn.close()
    return render_template('objects/new.html', types=types)


@app.route('/objects/edit_object/<int:object_id>', methods=['GET'])
def edit_object():
    # TODO: make sure object is a user type otherwise 404
    return
