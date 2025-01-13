from flask import Flask, render_template, request, url_for, redirect, make_response, get_template_attribute
import utils.database_functions as db

# >flask --app server run --debug --port 3000
app = Flask(__name__, static_url_path='/static')

def search_objects(search_string, filter, amnt):
    (conn, c) = db.get_cursor('data_catalog.db')
    db.query_search(c, search_string, filter)
    obj = c.fetchmany(amnt)
    conn.close()
    return obj


# [GET] return the full home page
@app.route('/', methods=['GET'])
def index():
    rendered_template = render_template('objects/index.html')
    response = make_response(rendered_template)
    response.status_code = 200
    return response


# [GET] returns a full page
#   a view of the objects as a table and a form for searching
# [POST] returns a partial
#   finds any objects matching the provided search parameters
#   and returns a table with rows being the matching objects
@app.route('/objects', methods=['GET', 'POST'])
def objects():
    if request.method == 'POST':
        search_string = request.form.get('search')
        filter = request.form.get('filter')
        obj = search_objects(search_string, filter, 50)

        rendered_template = render_template(
            'objects/_partials/search_results.html',
            obj=obj
        )
        response = make_response(rendered_template)
        response.status_code = 200
        return response

    # default to GET
    rendered_template = render_template('objects/index.html')
    response = make_response(rendered_template)
    response.status_code = 200
    return response


# [GET] returns a full page
#   a view of the object, with the provided id, and its related information
# [PATCH] returns a partial
#   updates the description of the object with give id
#   returns the div with the updated description
@app.route('/objects/<int:object_id>', methods=['GET', 'PATCH'])
def view_object(object_id):
    (conn, c) = db.get_cursor('data_catalog.db')

    if request.method == 'PATCH':
        desc = request.form.get('updated-desc')
        desc = db.sanatize(desc)

        db.query_object_desc_upsert(c, object_id, desc)
        conn.commit()

        db.query_object_info(c, object_id)
        obj = c.fetchone()

        conn.close()

        macro = get_template_attribute('_macros.html', 'object_header')
        response = make_response(macro(obj))
        response.status_code = 200
        return response

    # default to GET
    db.query_object_info(c, object_id)
    obj = c.fetchone()

    db.query_columns_info(c, object_id)
    cols = c.fetchall()

    db.query_indexes_info(c, object_id)
    idxs = c.fetchall()

    # Dependency information
    # A dummy with no parent is needed to act as the 'root' of the tree
    up_data = [{'name': obj[1], 'parent': '', 'id': obj[0]}]
    down_data = [{'name': obj[1], 'parent': '', 'id': obj[0]}]
    db.query_dependencies_upstream_recurse(c, object_id, 6)
    up = c.fetchall()
    for (parent_id, parent_name, child_id, child_name) in up:
        up_data.append({
            'name': child_name,
            'parent': parent_name,
            'id': child_id
        })
    db.query_dependencies_downstream_recurse(c, object_id, 6)
    down = c.fetchall()
    for (parent_id, parent_name, child_id, child_name) in down:
        down_data.append({
            'name': parent_name,
            'parent': child_name,
            'id': parent_id
        })

    conn.close()

    rendered_template = render_template(
        'view/index.html',
        obj=obj,
        cols=cols,
        idxs=idxs,
        up_data=up_data,
        down_data=down_data
    )
    response = make_response(rendered_template)
    response.status_code = 200
    return response


@app.route('/objects/column/<int:column_id>', methods=['PATCH'])
def edit_column_desc(column_id):
    (conn, c) = db.get_cursor('data_catalog.db')
    desc = request.form.get('updated-desc')
    desc = db.sanatize(desc)

    db.query_col_desc_upsert(c, column_id, desc)
    conn.commit()

    db.query_column_info(c, column_id)
    col = c.fetchone()

    conn.close()

    rendered_template = render_template(
        'view/_partials/show_column_row.html',
        col=col
    )
    response = make_response(rendered_template)
    response.status_code = 200
    return response


# [GET] return a partial
#   a row containing information about an object which another is dependent on
@app.route('/objects/new/add_dependency/<int:object_id>', methods=['GET'])
def add_dependency(object_id):
    print(object_id)
    (conn, c) = db.get_cursor('data_catalog.db')
    db.query_object_info(c, object_id)
    obj = c.fetchone()
    conn.close()
    rendered_template = render_template(
        'objects/new/_partials/search_add.html',
        obj=obj
    )
    response = make_response(rendered_template)
    response.status_code = 200
    return response


# [GET] returns a full page
#   a form for creating a new object
# [POST] returns a partial
#   if the request is from the search form:
#       then the search results are returned as table rows
#   if the request is from the creation form:
#       the object is created and redirects to that new objects page
@app.route('/objects/new', methods=['GET', 'POST'])
def new_object():
    # there are multiple elements that issue post requests to this route
    # each form contains a:
    #   <input type="hidden" name="form-id" value="{{ UNIQUE_IDENTIFIER }}"></input>
    # which determines which actions to take based on the value of the form-id
    if request.method == 'POST' and request.form.get('form-id') == "new-object-form":
        print(request.form)
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

        response = make_response()
        response.headers['Hx-Redirect'] = url_for('view_object', object_id=id)
        response.status_code = 200
        return response

    if request.method == 'POST' and request.form.get('form-id') == "search-form":
        print('search')
        search_string = request.form.get('search')
        filter = request.form.get('filter')
        obj = search_objects(search_string, filter, 50)
        rendered_template = render_template(
            'objects/new/_partials/search_results.html',
            obj=obj
        )
        response = make_response(rendered_template)
        response.status_code = 200
        return response

    # default GET
    (conn, c) = db.get_cursor('data_catalog.db')
    db.query_user_object_types(c)
    types = c.fetchall()
    conn.close()

    rendered_template = render_template('objects/new/index.html', types=types)
    response = make_response(rendered_template)
    response.status_code = 200
    return response


@app.route('/objects/edit_object/<int:object_id>', methods=['GET'])
def edit_object():
    # TODO: make sure object is a user type otherwise 404
    return
