from flask import Flask, render_template, request, url_for, redirect, make_response
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
    up_data = [{'name': obj[1], 'parent': '', 'id': obj[0]}]
    down_data = [{'name': obj[1], 'parent': '', 'id': obj[0]}]
    db.query_dependencies_upstream_recurse(c, object_id, 6)
    up = c.fetchall()
    for (parent_id, parent_name, child_id, child_name) in up:
        up_data.append({'name': child_name, 'parent': parent_name, 'id': child_id})
    print(down_data)
    db.query_dependencies_downstream_recurse(c, object_id, 6)
    down = c.fetchall()
    for (parent_id, parent_name, child_id, child_name) in down:
        down_data.append({'name': parent_name, 'parent': child_name, 'id': parent_id})
    print(up_data)

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


@app.route('/objects/new_object', methods=['GET', 'POST'])
def new_object():
    if request.method == 'POST':
        object_name = db.sanatize(request.form.get('object-name'))
        object_type = db.sanatize(request.form.get('object-type'))
        object_owner = request.form.get('object-owner')
        if object_owner is not None:
            object_owner = db.sanatize(object_owner)
        object_developer = request.form.get('object-developer')
        if object_developer is not None:
            object_developer = db.sanatize(object_developer)
        object_description = request.form.get('object-description')
        if object_description is not None:
            object_description = db.sanatize(object_description)
        dependencies = []
        for f in request.form:
            if f.startswith("dependency"):
                dependencies.append(int(request.form.get(f)))
        print(object_name)
        print(object_type)
        print(object_owner)
        print(object_developer)
        print(object_description)
        print(dependencies)

        (conn, c) = db.get_cursor('data_catalog.db')
        id = db.query_add_object(c, object_name, object_type, object_description, dependencies)
        print("OOOOOOOOOOOOOOOOOOOOOOOOOOO", id)
        conn.commit()

        #TODO: Make sure the name isn't already in the table??
        '''
            add the new item into the objects table
                name = object_name
                type = lookup id of object_type in object_types
                is_hidden = 0
            get the id of the new object
                * from objects where name == object_name

            add the description to object_descriptions table
                object id = id
                description = object_description

            add the dependencies
                parent = dependency[i]
                child = id
        '''

        response = make_response()
        response.headers['Hx-Redirect'] = url_for('view', object_id=id)
        return response

    # default GET
    (conn, c) = db.get_cursor('data_catalog.db')
    db.query_user_object_types(c)
    types = c.fetchall()
    conn.close()
    return render_template('objects/new.html', types=types)


@app.route('/objects/edit_object/<int:object_id>', methods=['GET'])
def edit_object():
    # TODO: make sure object is a user type otherwise 404
    return
