import sqlite3


def create_database():
    conn = sqlite3.connect('data_catalog.db')
    c = conn.cursor()

    # Table for object types
    c.execute('''
        CREATE TABLE IF NOT EXISTS object_types (
            id INTEGER PRIMARY KEY AUTOINCREMENT
            , type_name TEXT UNIQUE NOT NULL
        )
    ''')

    # Table for objects (tables, views, SSRS, PBI, SPs)
    c.execute('''
        CREATE TABLE IF NOT EXISTS objects (
            id INTEGER PRIMARY KEY AUTOINCREMENT
            , name TEXT UNIQUE NOT NULL
            , type INTEGER NOT NULL
            , is_hidden INTEGER NOT NULL

            , CHECK (is_hidden IN (0,1))
            , FOREIGN KEY(type) REFERENCES object_types(id)
        )
    ''')

    # Table for Columns
    c.execute('''
        CREATE TABLE IF NOT EXISTS columns (
            id INTEGER PRIMARY KEY AUTOINCREMENT
            , object_id INTEGER NOT NULL
            , name TEXT NOT NULL
            , type TEXT NOT NULL
            , length INTEGER
            , precision INTEGER
            , scale INTEGER
            , is_nullable INTEGER NOT NULL

            , CHECK (is_nullable IN (0,1))
            , FOREIGN KEY(object_id) REFERENCES objects(id)
        )
    ''')

    c.execute('''
        CREATE TABLE IF NOT EXISTS indexes (
            id INTEGER PRIMARY KEY AUTOINCREMENT
            , object_id INTEGER NOT NULL
            , name TEXT NOT NULL
            , type TEXT NOT NULL
            , is_primary_key INTEGER NOT NULL

            , CHECK (is_primary_key IN (0,1))
            , FOREIGN KEY(object_id) REFERENCES objects(id)
        )
    ''')

    c.execute('''
        CREATE TABLE IF NOT EXISTS object_descriptions (
            object_id INTEGER NOT NULL
            , description TEXT

            , PRIMARY KEY (object_id)
            , FOREIGN KEY(object_id) REFERENCES objects(id)
        )
    ''')

    c.execute('''
        CREATE TABLE IF NOT EXISTS column_descriptions (
            column_id INTEGER PRIMARY KEY UNIQUE NOT NULL
            , description TEXT

            , FOREIGN KEY(column_id) REFERENCES columns(id)
        )
    ''')

    c.execute('''
        CREATE TABLE IF NOT EXISTS relationships (
            id INTEGER PRIMARY KEY AUTOINCREMENT
            , parent_id INTEGER NOT NULL
            , child_id INTEGER NOT NULL

            , FOREIGN KEY(parent_id) REFERENCES objects(id)
            , FOREIGN KEY(child_id) REFERENCES objects(id)
        )
    ''')


def query_database():
    conn = sqlite3.connect('data_catalog.db')
    c = conn.cursor()
    c.execute('''SELECT * FROM object_types LIMIT 5''')
    print("object_types\n\t", c.fetchall())

    c.execute('''SELECT * FROM objects LIMIT 5''')
    print("objects\n\t", c.fetchall())

    c.execute('''SELECT * FROM columns LIMIT 5''')
    print("columns\n\t", c.fetchall())

    c.execute('''SELECT * FROM indexes LIMIT 5''')
    print("indexes\n\t", c.fetchall())

    c.execute('''SELECT * FROM object_descriptions LIMIT 5''')
    print("object_descriptions\n\t", c.fetchall())

    c.execute('''SELECT * FROM column_descriptions LIMIT 5''')
    print("column_descriptions\n\t", c.fetchall())

    c.execute('''SELECT * FROM relationships LIMIT 5''')
    print("relationships\n\t", c.fetchall())


def wipe_database():
    conn = sqlite3.connect('data_catalog.db')
    c = conn.cursor()

    c.execute('''DROP TABLE IF EXISTS object_descriptions''')
    c.execute('''DROP TABLE IF EXISTS column_descriptions''')
    c.execute('''DROP TABLE IF EXISTS relationships''')
    c.execute('''DROP TABLE IF EXISTS indexes''')
    c.execute('''DROP TABLE IF EXISTS columns''')
    c.execute('''DROP TABLE IF EXISTS objects''')
    c.execute('''DROP TABLE IF EXISTS object_types''')

    conn.commit()


def add_base_data():
    conn = sqlite3.connect('data_catalog.db')
    c = conn.cursor()

    c.execute('''
        INSERT INTO object_types
            (type_name)
        VALUES
            ("Table")
            , ("View")
            , ("Stored Procedure")
            , ("PowerBI")
            , ("SSRS")
    ''')

    c.execute('''
        INSERT INTO objects
            (name, type, is_hidden)
        VALUES
            ("table A", 1, 0)
            , ("table B", 1, 0)
            , ("table C", 1, 0)
            , ("table D", 1, 0)
            , ("table E", 1, 0)
            , ("table F", 1, 0)
            , ("table G", 1, 0)
            , ("table H", 1, 0)
            , ("View A", 2, 0)
            , ("View B", 2, 0)
            , ("View C", 2, 0)
            , ("View D", 2, 0)
            , ("View E", 2, 0)
            , ("View F", 2, 0)
            , ("View G", 2, 0)
            , ("View H", 2, 0)
            , ("SP A", 3, 0)
            , ("SP B", 3, 0)
            , ("SP C", 3, 0)
            , ("SP D", 3, 0)
            , ("SP E", 3, 0)
            , ("SP F", 3, 0)
            , ("SP G", 3, 0)
            , ("SP H", 3, 0)
            , ("PBI A", 4, 0)
            , ("PBI B", 4, 0)
            , ("PBI C", 4, 0)
            , ("PBI D", 4, 0)
            , ("PBI E", 4, 0)
            , ("PBI F", 4, 0)
            , ("PBI G", 4, 0)
            , ("PBI H", 4, 0)
            , ("SSRS A", 5, 0)
            , ("SSRS B", 5, 0)
            , ("SSRS C", 5, 0)
            , ("SSRS D", 5, 0)
            , ("SSRS E", 5, 0)
            , ("SSRS F", 5, 0)
            , ("SSRS G", 5, 0)
            , ("SSRS H", 5, 0)
    ''')

    c.execute('''
        INSERT INTO columns
            (object_id, name, type, length, precision, scale, is_nullable)
        VALUES
            (1, "column1", "text", 32, 0, 0, 0)
            , (1, "column2", "text", 32, 0, 1, 1)
            , (1, "column3", "int", 38, 2, 3, 0)
            , (1, "column4", "bool", 2, 4, 5, 1)
            , (1, "column5", "datetime", 16, 6, 7, 0)
            , (1, "column5", "datetime", 16, 6, 7, 0)
            , (9, "column1", "text", 16, 0, 0, 0)
            , (9, "column2", "text", 16, 0, 1, 1)
            , (9, "column3", "int", 32, 2, 3, 0)
            , (9, "column4", "bool", 8, 4, 5, 1)
            , (9, "column5", "datetime", 10, 6, 7, 0)
            , (9, "column5", "datetime", 12, 6, 7, 0)
    ''')

    c.execute('''
        INSERT INTO indexes
            (object_id, name, type, is_primary_key)
        VALUES
            (1, "index1", "clustered", 1)
            , (1, "index2", "heap", 0)
            , (1, "index3", "non-clustered", 0)
    ''')

    c.execute('''
        INSERT INTO object_descriptions
            (object_id, description)
        VALUES
            (1, "placeholder description")
            , (2, "placeholder description")
            , (3, "placeholder description")
            , (4, "placeholder description")
            , (5, "placeholder description")
            , (9, "placeholder description")
            , (10, "placeholder description")
            , (17, "placeholder description")
            , (25, "placeholder description")
            , (33, "placeholder description")
    ''')

    c.execute('''
        INSERT INTO column_descriptions
            (column_id, description)
        VALUES
            (1, "placeholder description")
            , (3, "placeholder description")
            , (8, "placeholder description")
            , (11, "placeholder description")
    ''')

    c.execute('''
        INSERT INTO relationships
            (parent_id, child_id)
        VALUES
            (7,3)
            , (6,3)
            , (3,1)
            , (1,2)
            , (2,4)
            , (2,5)
            , (2,8)
    ''')

    conn.commit()


if __name__ == "__main__":
    wipe_database()
    create_database()
    add_base_data()
    query_database()
