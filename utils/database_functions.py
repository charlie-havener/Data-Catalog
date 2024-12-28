import sqlite3


def get_cursor(db):
    conn = sqlite3.connect(db)
    c = conn.cursor()
    return (conn, c)


def sanatize(text):
    out = []
    for char in text:
        if char == '\\':
            out.append("\\\\")
        elif char == '\'':
            out.append('\\\'')
        elif char == '\"':
            out.append('\\\"')
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


def query_dependencies_upstream(cursor, ids):
    cursor.execute('''
        SELECT
            r.parent_id
            , o.name
            , r.child_id
            , o2.name
        FROM relationships as r
        LEFT JOIN objects as o
        ON r.parent_id = o.id
        LEFT JOIN objects as o2
        ON r.child_id = o2.id
        WHERE parent_id IN (%s)
        ''' % ','.join('?' * len(ids)), ids)
    return


def query_dependencies_downstream(cursor, ids):
    cursor.execute('''
        SELECT
            r.parent_id
            , o.name
            , r.child_id
            , o2.name
        FROM relationships as r
        LEFT JOIN objects as o
        ON r.parent_id = o.id
        LEFT JOIN objects as o2
        ON r.child_id = o2.id
        WHERE child_id IN (%s)
        ''' % ','.join('?' * len(ids)), ids)
    return
