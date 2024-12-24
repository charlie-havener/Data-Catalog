import sqlite3


# if test.db it will be created if it doesn't already exist
# after the tables will be added if they don't already exist
def create_database():
    conn = sqlite3.connect('database_objects.db')
    c = conn.cursor()

    # create the table of Objects (tables, views, stored_procedures)
    c.execute('''
        CREATE TABLE IF NOT EXISTS objects (
            database_id INTEGER NOT NULL
            , database_name TEXT NOT NULL
            , object_id INTEGER NOT NULL
            , object_name TEXT NOT NULL
            , schema_id INTEGER NOT NULL
            , schema_name TEXT NOT NULL
            , type TEXT NOT NULL
            , type_desc TEXT NOT NULL
            , object_create_date TEXT NOT NULL

            , PRIMARY KEY (database_id, object_id)
        )
        ''')
    conn.commit()

    # create the table of Columns
    c.execute('''
        CREATE TABLE IF NOT EXISTS columns (
            database_id INTEGER NOT NULL
            , database_name TEXT NOT NULL
            , object_id INTEGER NOT NULL
            , column_id INTEGER NOT NULL
            , column_name TEXT NOT NULL
            , type_id INTEGER NOT NULL
            , type_name TEXT NOT NULL
            , max_length INTEGER NOT NULL
            , precision INTEGER NOT NULL
            , scale INTEGER NOT NULL
            , is_nullable INT NOT NULL

            , PRIMARY KEY (database_id, object_id, column_id)
        )
        ''')
    conn.commit()

    # create the table of Indexes
    c.execute('''
        CREATE TABLE IF NOT EXISTS indexes (
            database_id INTEGER NOT NULL
            , database_name TEXT NOT NULL
            , object_id INTEGER NOT NULL
            , index_id INTEGER NOT NULL
            , index_name TEXT NOT NULL
            , type_id INT NOT NULL
            , type_name TEXT NOT NULL
            , is_primary_key INT NOT NULL

            , PRIMARY KEY (database_id, object_id, index_id)
        )
        ''')
    conn.commit()

    # create the table of Index Columns
    c.execute('''
        CREATE TABLE IF NOT EXISTS index_columns (
            database_id INTEGER NOT NULL
            , database_name TEXT NOT NULL
            , object_id INTEGER NOT NULL
            , object_name TEXT NOT NULL
            , index_id INTEGER NOT NULL
            , index_name TEXT NOT NULL
            , index_col_id INTEGER NOT NULL
            , object_col_name TEXT NOT NULL
            , is_included_column INTEGER NOT NULL

            , PRIMARY KEY (database_id, object_id, index_id, index_col_id)
        )
        ''')
    conn.commit()

    # create the table for object descriptions
    c.execute('''
        CREATE TABLE IF NOT EXISTS object_descriptions (
            database_id INTEGER NOT NULL
            , object_id INTEGER NOT NULL
            , description

            , PRIMARY KEY (database_id, object_id)
        )
        ''')
    conn.commit()

    # create the table for column descriptions
    c.execute('''
        CREATE TABLE IF NOT EXISTS column_descriptions (
            database_id INTEGER NOT NULL
            , object_id INTEGER NOT NULL
            , column_id INTEGER NOT NULL
            , description

            , PRIMARY KEY (database_id, object_id, column_id)
        )
        ''')
    conn.commit()

    # TODO: create the table of Relationships and create a viewable DAG
    c.execute('''
        CREATE TABLE IF NOT EXISTS dependencies (
            parent_id INTEGER NOT NULL
            , child_id INTEGER NOT NULL
        )
        ''')

    conn.close()


def query_database():
    conn = sqlite3.connect('database_objects.db')
    c = conn.cursor()

    c.execute('''SELECT * FROM objects LIMIT 5''')
    print("objects\n\t", c.fetchall())

    c.execute('''SELECT * FROM columns LIMIT 5''')
    print("columns\n\t", c.fetchall())

    c.execute('''SELECT * FROM indexes LIMIT 5''')
    print("indexes\n\t", c.fetchall())

    c.execute('''SELECT * FROM index_columns LIMIT 5''')
    print("index_columns\n\t", c.fetchall())

    c.execute('''SELECT * FROM object_descriptions LIMIT 5''')
    print("object_descriptions\n\t", c.fetchall())

    c.execute('''SELECT * FROM column_descriptions LIMIT 5''')
    print("column_descriptions\n\t", c.fetchall())

    c.execute('''SELECT * FROM dependencies LIMIT 5''')
    print("dependencies\n\t", c.fetchall())

    conn.close()


def reset_data():
    conn = sqlite3.connect('database_objects.db')
    c = conn.cursor()

    # delete all the current data
    c.execute('''DELETE FROM objects''')
    c.execute('''DELETE FROM columns''')
    c.execute('''DELETE FROM indexes''')
    c.execute('''DELETE FROM index_columns''')
    c.execute('''DELETE FROM object_descriptions''')
    c.execute('''DELETE FROM column_descriptions''')
    c.execute('''DELETE FROM dependencies''')
    conn.commit()

    # add some row
    c.execute('''INSERT INTO objects VALUES (?,?,?,?,?,?,?,?,?)''', (1,'ERP',1,'Locations',1,'dbo','U','table','1/1/2024'))
    c.execute('''INSERT INTO objects VALUES (?,?,?,?,?,?,?,?,?)''', (1,'ERP',2,'Warehouses',1,'dbo','U','table','1/1/2024'))
    c.execute('''INSERT INTO objects VALUES (?,?,?,?,?,?,?,?,?)''', (1,'ERP',3,'vw_WarehouseLocations',1,'dbo','V','view','1/1/2024'))
    c.execute('''INSERT INTO objects VALUES (?,?,?,?,?,?,?,?,?)''', (1,'ERP',4,'sp_GetIDs',2,'tst','P','stored procedure','1/1/2024'))
    c.execute('''INSERT INTO objects VALUES (?,?,?,?,?,?,?,?,?)''', (1,'ERP',5,'Items',1,'dbo','U','table','1/1/2024'))
    c.execute('''INSERT INTO objects VALUES (?,?,?,?,?,?,?,?,?)''', (2,'CATSWeb',1,'Tasks',1,'app','U','table','1/1/2024'))
    c.execute('''INSERT INTO objects VALUES (?,?,?,?,?,?,?,?,?)''', (2,'CATSWeb',2,'Subtasks',1,'app','U','table','1/1/2024'))
    c.execute('''INSERT INTO objects VALUES (?,?,?,?,?,?,?,?,?)''', (2,'CATSWeb',3,'vw_AllActions',1,'app','V','view','1/1/2024'))

    c.execute('''INSERT INTO columns VALUES (?,?,?,?,?,?,?,?,?,?,?)''', (1,'ERP',1,1,'location_name',100,'varchar',16,0,0,0))
    c.execute('''INSERT INTO columns VALUES (?,?,?,?,?,?,?,?,?,?,?)''', (1,'ERP',1,2,'location_id',200,'int',32,0,0,0))
    c.execute('''INSERT INTO columns VALUES (?,?,?,?,?,?,?,?,?,?,?)''', (1,'ERP',1,3,'location_desc',100,'varchar',64,0,0,1))
    c.execute('''INSERT INTO columns VALUES (?,?,?,?,?,?,?,?,?,?,?)''', (1,'ERP',2,1,'warehouse_name',100,'varchar',16,0,0,0))
    c.execute('''INSERT INTO columns VALUES (?,?,?,?,?,?,?,?,?,?,?)''', (1,'ERP',2,2,'warehouse_id',200,'int',32,0,0,0))
    c.execute('''INSERT INTO columns VALUES (?,?,?,?,?,?,?,?,?,?,?)''', (1,'ERP',2,3,'warehouse_desc',100,'varchar',64,0,0,1))
    c.execute('''INSERT INTO columns VALUES (?,?,?,?,?,?,?,?,?,?,?)''', (1,'ERP',3,1,'warehouse_id',200,'int',32,0,0,0))
    c.execute('''INSERT INTO columns VALUES (?,?,?,?,?,?,?,?,?,?,?)''', (1,'ERP',3,2,'location_id',200,'int',32,0,0,0))
    c.execute('''INSERT INTO columns VALUES (?,?,?,?,?,?,?,?,?,?,?)''', (1,'ERP',3,3,'location_name',100,'varchar',16,0,0,0))
    c.execute('''INSERT INTO columns VALUES (?,?,?,?,?,?,?,?,?,?,?)''', (1,'ERP',3,4,'warehouse_name',100,'varchar',16,0,0,0))
    c.execute('''INSERT INTO columns VALUES (?,?,?,?,?,?,?,?,?,?,?)''', (1,'ERP',5,1,'item_id',200,'int',32,0,0,0))
    c.execute('''INSERT INTO columns VALUES (?,?,?,?,?,?,?,?,?,?,?)''', (1,'ERP',5,2,'item_name',100,'varchar',64,0,0,0))
    c.execute('''INSERT INTO columns VALUES (?,?,?,?,?,?,?,?,?,?,?)''', (1,'ERP',5,3,'item_price',300,'decimal',32,24,8,0))
    c.execute('''INSERT INTO columns VALUES (?,?,?,?,?,?,?,?,?,?,?)''', (2,'CATSWeb',1,1,'task_id',200,'int',32,0,0,0))
    c.execute('''INSERT INTO columns VALUES (?,?,?,?,?,?,?,?,?,?,?)''', (2,'CATSWeb',1,2,'task_name',100,'nvarchar',128,0,0,0))
    c.execute('''INSERT INTO columns VALUES (?,?,?,?,?,?,?,?,?,?,?)''', (2,'CATSWeb',2,1,'subtask_id',200,'int',32,0,0,0))
    c.execute('''INSERT INTO columns VALUES (?,?,?,?,?,?,?,?,?,?,?)''', (2,'CATSWeb',2,2,'subtask_name',100,'nvarchar',128,0,0,0))
    c.execute('''INSERT INTO columns VALUES (?,?,?,?,?,?,?,?,?,?,?)''', (2,'CATSWeb',3,1,'task_id',200,'int',32,0,0,0))
    c.execute('''INSERT INTO columns VALUES (?,?,?,?,?,?,?,?,?,?,?)''', (2,'CATSWeb',3,2,'subtask_id',200,'int',32,0,0,0))
    c.execute('''INSERT INTO columns VALUES (?,?,?,?,?,?,?,?,?,?,?)''', (2,'CATSWeb',3,3,'task_name',100,'nvarchar',128,0,0,0))
    c.execute('''INSERT INTO columns VALUES (?,?,?,?,?,?,?,?,?,?,?)''', (2,'CATSWeb',3,4,'subtask_name',100,'nvarchar',128,0,0,0))

    c.execute('''INSERT INTO indexes VALUES (?,?,?,?,?,?,?,?)''', (1,'ERP',1,1,'PK_Locations','C','clustered',1))
    c.execute('''INSERT INTO indexes VALUES (?,?,?,?,?,?,?,?)''', (1,'ERP',2,2,'PK_Warehouses','C','clustered',1))
    c.execute('''INSERT INTO indexes VALUES (?,?,?,?,?,?,?,?)''', (1,'ERP',5,3,'PK_Items','C','clustered',1))
    c.execute('''INSERT INTO indexes VALUES (?,?,?,?,?,?,?,?)''', (1,'ERP',5,4,'IDX_Item_Price','N','non-clustered',0))
    c.execute('''INSERT INTO indexes VALUES (?,?,?,?,?,?,?,?)''', (2,'CATSWeb',1,9,'PK_Tasks','C','clustered',1))
    c.execute('''INSERT INTO indexes VALUES (?,?,?,?,?,?,?,?)''', (2,'CATSWeb',2,10,'PK_Subtasks','C','clustered',1))
    c.execute('''INSERT INTO indexes VALUES (?,?,?,?,?,?,?,?)''', (2,'CATSWeb',2,11,'IDX_SubtaskName','N','non-clustered',0))

    c.execute('''INSERT INTO index_columns VALUES (?,?,?,?,?,?,?,?,?)''', (1,'ERP',1,'Locations',1,'PK_Locations',1,'location_id',0))
    c.execute('''INSERT INTO index_columns VALUES (?,?,?,?,?,?,?,?,?)''', (1,'ERP',2,'Warehouses',2,'PK_Warehouses',1,'warehouse_id',0))
    c.execute('''INSERT INTO index_columns VALUES (?,?,?,?,?,?,?,?,?)''', (1,'ERP',5,'Items',3,'PK_Items',1,'item_id',0))
    c.execute('''INSERT INTO index_columns VALUES (?,?,?,?,?,?,?,?,?)''', (1,'ERP',5,'Items',4,'IDX_Item_Price',1,'item_price',0))
    c.execute('''INSERT INTO index_columns VALUES (?,?,?,?,?,?,?,?,?)''', (1,'ERP',5,'Items',4,'IDX_Item_Price',2,'item_id',0))
    c.execute('''INSERT INTO index_columns VALUES (?,?,?,?,?,?,?,?,?)''', (1,'ERP',5,'Items',4,'IDX_Item_Price',3,'item_name',1))
    c.execute('''INSERT INTO index_columns VALUES (?,?,?,?,?,?,?,?,?)''', (2,'CATSWeb',1,'Tasks',9,'PK_Tasks',1,'task_id',0))
    c.execute('''INSERT INTO index_columns VALUES (?,?,?,?,?,?,?,?,?)''', (2,'CATSWeb',2,'Subtasks',10,'PK_Subtasks',1,'subtask_id',0))
    c.execute('''INSERT INTO index_columns VALUES (?,?,?,?,?,?,?,?,?)''', (2,'CATSWeb',2,'Subtasks',11,'IDX_SubtaskName',1,'subtask_name',0))
    c.execute('''INSERT INTO index_columns VALUES (?,?,?,?,?,?,?,?,?)''', (2,'CATSWeb',2,'Subtasks',11,'IDX_SubtaskName',2,'subtask_id',1))

    c.execute('''INSERT INTO object_descriptions VALUES (?,?,?)''', (1,1,'ERP-Locations-Description'))
    c.execute('''INSERT INTO object_descriptions VALUES (?,?,?)''', (1,2,'really really really really really really really really really really really really really really really really really really really really really really really really really really long description'))

    c.execute('''INSERT INTO dependencies VALUES(?,?)''', (6,2))
    c.execute('''INSERT INTO dependencies VALUES(?,?)''', (5,2))
    c.execute('''INSERT INTO dependencies VALUES(?,?)''', (2,0))
    c.execute('''INSERT INTO dependencies VALUES(?,?)''', (0,1))
    c.execute('''INSERT INTO dependencies VALUES(?,?)''', (1,3))
    c.execute('''INSERT INTO dependencies VALUES(?,?)''', (1,4))
    c.execute('''INSERT INTO dependencies VALUES(?,?)''', (1,7))

    conn.commit()

    return ''


if __name__ == "__main__":
    create_database()
    reset_data()
    query_database()
