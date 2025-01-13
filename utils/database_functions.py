import sqlite3
from itertools import repeat


def get_cursor(db):
    conn = sqlite3.connect(db)
    c = conn.cursor()
    return (conn, c)


def sanatize(text):
    out = []
    for char in text:
        if char == '&':
            out.append("&amp")
        elif char == '<':
            out.append('&lt')
        elif char == '>':
            out.append('&gt')
        elif char == '"':
            out.append('&quot')
        elif char == "'":
            out.append('&#x27')
        elif char == '/':
            out.append('&#x2F')
        elif char == '`':
            out.append('&grave')
        elif char == '=':
            out.append('&#x3D')
        else:
            out.append(char)
    return "".join(x for x in out)


def query_search(cursor, search_string, filter):

    if filter == "All":
        predicate = ""
        param_list = ('%' + search_string + '%',)
    else:
        predicate = 'AND type = ?'
        param_list = ('%' + search_string + '%', int(filter),)

    cursor.execute('''
        SELECT
            o.id
            , o.name
            , ot.type_name
            , od.description
        FROM
            objects as o
        LEFT JOIN
            object_descriptions as od
        ON
            o.id = od.object_id
        LEFT JOIN
            object_types as ot
        ON
            o.type = ot.id
        WHERE
            o.name LIKE ?''' + predicate, param_list)
    return


def query_object_info(cursor, object_id):
    cursor.execute('''
        SELECT
            o.id
            , o.name
            , ot.type_name
            , od.description
            , ot.source
        FROM
            objects as o
        LEFT JOIN
            object_descriptions as od
        ON
            o.id = od.object_id
        LEFT JOIN
            object_types as ot
        ON
            o.type = ot.id
        WHERE
            o.id = ?
        ''', (object_id,))
    return


def query_columns_info(cursor, object_id):
    cursor.execute('''
        SELECT
            c.id
            , c.name
            , c.type
            , c.length
            , c.precision
            , c.scale
            , c.is_nullable
            , cd.description
        FROM
            columns as c
        LEFT JOIN
            column_descriptions as cd
        ON
            c.id = cd.column_id
        WHERE
            c.object_id = ?
        ''', (object_id,))
    return


def query_column_info(cursor, column_id):
    cursor.execute('''
        SELECT
            c.id
            , c.name
            , c.type
            , c.length
            , c.precision
            , c.scale
            , c.is_nullable
            , cd.description
        FROM
            columns as c
        LEFT JOIN
            column_descriptions as cd
        ON
            c.id = cd.column_id
        WHERE
            c.id = ?
        ''', (column_id,))
    return


def query_indexes_info(cursor, object_id):
    cursor.execute('''
        SELECT
            i.id
            , i.name
            , i.type
            , i.is_primary_key
        FROM
            indexes as i
        WHERE
            i.object_id = ?
        ''', (object_id,))
    return


def query_object_desc_upsert(cursor, object_id, new_description):
    cursor.execute('''
        INSERT INTO object_descriptions (object_id, description)
        VALUES (?1,?2)
        ON CONFLICT (object_id)
        DO UPDATE SET description = ?2
        ''', (object_id, new_description,))
    return


def query_col_desc_upsert(cursor, column_id, new_description):
    cursor.execute('''
        INSERT INTO column_descriptions (column_id, description)
        VALUES (?1,?2)
        ON CONFLICT (column_id)
        DO UPDATE SET
            description = ?2
        ''', (column_id, new_description,))
    return


def query_dependencies_downstream_recurse(cursor, parent_id, depth):
    cursor.execute('''
        WITH RECURSIVE heirarchy as (
            SELECT parent_id, o.name as parent_name, child_id, o2.name as child_name, 1 as depth
            FROM relationships r
            LEFT JOIN objects o
            ON r.parent_id = o.id
            LEFT JOIN objects o2
            ON r.child_id = o2.id
            WHERE child_id = ?1

            UNION ALL

            SELECT r.parent_id, o.name, r.child_id, o2.name, h.depth+1
            FROM relationships r
            JOIN heirarchy h
            ON h.parent_id = r.child_id
                AND h.depth < ?2
            LEFT JOIN objects o
            ON r.parent_id = o.id
            LEFT JOIN objects o2
            ON r.child_id = o2.id
        )
        SELECT DISTINCT parent_id, parent_name, child_id, child_name FROM heirarchy
    ''', (parent_id, depth,))


def query_dependencies_upstream_recurse(cursor, parent_id, depth):
    cursor.execute('''
        WITH RECURSIVE heirarchy as (
            SELECT parent_id, o.name as parent_name, child_id, o2.name as child_name, 1 as depth
            FROM relationships r
            LEFT JOIN objects o
            ON r.parent_id = o.id
            LEFT JOIN objects o2
            ON r.child_id = o2.id
            WHERE parent_id = ?1

            UNION ALL

            SELECT r.parent_id, o.name, r.child_id, o2.name, h.depth+1
            FROM relationships r
            JOIN heirarchy h
            ON h.child_id = r.parent_id
                AND h.depth < ?2
            LEFT JOIN objects o
            ON r.parent_id = o.id
            LEFT JOIN objects o2
            ON r.child_id = o2.id
        )
        SELECT DISTINCT parent_id, parent_name, child_id, child_name FROM heirarchy
    ''', (parent_id, depth,))


def query_user_object_types(cursor):
    cursor.execute('''
        SELECT
            type_name
        FROM
            object_types
        WHERE
            source = "user"
        ORDER BY
            type_name
    ''')
    return


def query_add_object(cursor, object_name, object_type, object_description, dependencies):
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

    # add the new item to the objects table
    cursor.execute('''
        INSERT INTO objects (name, type, is_hidden)
        SELECT
            ?1
            , id
            , 0
        FROM object_types
        WHERE type_name = ?2
        RETURNING id
        ''', (object_name, object_type,))
    object_id = cursor.fetchone()[0]

    # add the description
    cursor.execute('''
        INSERT INTO object_descriptions (object_id, description)
        VALUES (?,?)
        ''', (object_id, object_description))

    dependencies = list(zip(dependencies, repeat(object_id)))
    print(dependencies)
    # add the dependencies
    cursor.executemany('''
        INSERT INTO relationships (parent_id, child_id)
        VALUES (?, ?)
        ''', dependencies)
    


    return object_id
