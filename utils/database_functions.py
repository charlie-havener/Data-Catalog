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
        param_list = ('%' + search_string + '%', filter,)

    cursor.execute('''
        SELECT
            o.database_id
            , o.object_id
            , o.database_name
            , o.schema_name
            , o.object_name
            , o.type_desc
            , od.description
        FROM objects as o
        LEFT JOIN object_descriptions as od
        ON
            o.database_id = od.database_id
            AND o.object_id = od.object_id
        WHERE
            object_name LIKE ?''' + predicate, param_list)
    return


def query_object_info(cursor, database_id, object_id):
    cursor.execute('''
        SELECT
            o.database_id
            , o.object_id
            , o.database_name
            , o.schema_name
            , o.object_name
            , o.type
            , o.type_desc
            , od.description
        FROM objects as o
        LEFT JOIN object_descriptions as od
            ON o.database_id = od.database_id
                AND o.object_id = od.database_id
        WHERE
            o.database_id = ?
            AND o.object_id = ?
        ''', (database_id, object_id,))
    return


def query_columns_info(cursor, database_id, object_id):
    cursor.execute('''
        SELECT
            c.column_id
            , c.column_name
            , c.type_name
            , cd.description
        FROM columns as c
        LEFT JOIN column_descriptions as cd
            ON c.database_id = cd.database_id
                AND c.object_id = cd.object_id
                AND c.column_id = cd.column_id
        WHERE
            c.database_id = ?
            AND c.object_id = ?
        ''', (database_id, object_id,))
    return


def query_column_info(cursor, database_id, object_id, column_id):
    cursor.execute('''
        SELECT
            c.database_id
            , c.object_id
            , c.column_id
            , c.column_name
            , c.type_name
            , cd.description
        FROM columns as c
        LEFT JOIN column_descriptions as cd
            ON c.database_id = cd.database_id
                AND c.object_id = cd.object_id
                AND c.column_id = cd.column_id
        WHERE
            c.database_id = ?
            AND c.object_id = ?
            AND c.column_id = ?
        ''', (database_id, object_id, column_id))
    return


def query_indexes_info(cursor, database_id, object_id):
    cursor.execute('''
        SELECT
            i.index_id
            , i.index_name
            , i.type_name
            , i.is_primary_key
        FROM indexes as i
        WHERE
            i.database_id = ?
            AND i.object_id = ?
        ''', (database_id, object_id,))
    return


def query_col_desc_upsert(cursor, database_id, object_id, column_id, new_description):
    cursor.execute('''
        INSERT INTO column_descriptions (database_id, object_id, column_id, description)
        VALUES (?1,?2,?3,?4)
        ON CONFLICT (database_id, object_id, column_id)
        DO UPDATE SET
            description = ?4
        ''', (database_id, object_id, column_id, new_description,))
    return
