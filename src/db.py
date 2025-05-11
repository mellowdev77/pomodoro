import sqlite3

def create_tables():
    # create connection to database
    cnt = sqlite3.connect('config.db')

    # Create a CONFIG TABLE
    cnt.execute('''CREATE TABLE IF NOT EXISTS CONFIG(
    create_actions INTEGER,
    load_new_quote INTEGER,
    change_default_quote INTEGER,
    timers_wait_for_user INTEGER,
    timers_based_on_average INTEGER,
    change_default_timers INTEGER);''')

    # Create a AVERAGE_RATIO TABLE
    cnt.execute('''CREATE TABLE IF NOT EXISTS AVERAGE_RATIO(
    average_round_length REAL,
    average_round_count REAL,
    average_break_length REAL,
    average_break_count REAL);''')

    # Create a ACTIONS TABLE
    cnt.execute('''CREATE TABLE IF NOT EXISTS ACTIONS(actions TEXT);''')

    # Create a DEFAULT_LENGTH TABLE
    cnt.execute('''CREATE TABLE IF NOT EXISTS DEFAULT_LENGTH(
    default_round_length REAL,
    default_break_length REAL);''')

    # Create a DEFAULT_QUOTE TABLE
    cnt.execute('''CREATE TABLE IF NOT EXISTS DEFAULT_QUOTE(default_quote TEXT);''')
    cnt.commit()
    cnt.close()

def insert_default_values(empty_tables):
    # create connection to database
    cnt = sqlite3.connect('config.db')
    for table in empty_tables:
        match table:
            case "CONFIG":
                cnt.execute('''INSERT INTO CONFIG VALUES(0,1,0,1,0,0)''')
            case "ACTIONS":
                cnt.execute('''INSERT INTO ACTIONS VALUES('Meditate'),('Jumping Jacks'),('Pushups'),('Squats'),('Walk the dogs'),('Read a book'),('Go outside')''')
            case "AVERAGE_RATIO":
                cnt.execute('''INSERT INTO AVERAGE_RATIO VALUES(25,1,5,1)''')
            case "DEFAULT_LENGTH":
                cnt.execute('''INSERT INTO DEFAULT_LENGTH VALUES(25,5)''')
            case "DEFAULT_QUOTE":
                cnt.execute('''INSERT INTO DEFAULT_QUOTE VALUES('Chop wood, carry water.')''')

    # Query the data
    cnt.commit()
    cnt.close()

def insert_into_table(table, values):
    # create connection to database
    cnt = sqlite3.connect('config.db')
    cnt.execute(f"INSERT INTO {table} VALUES('{values}')")

    # Query the data
    cnt.commit()
    cnt.close()

def update_table(table, row, value):
    # create connection to database
    cnt = sqlite3.connect('config.db')

    cnt.execute(f"UPDATE {table} SET {row} = '{value}'")
    cnt.commit()
    cnt.close()

def drop_tables():
    cnt = sqlite3.connect('config.db')
    tables = ["ACTIONS", "CONFIG", "DEFAULT_LENGTH", "DEFAULT_QUOTE", "AVERAGE_RATIO"]
    for table in tables:
        cnt.execute(f"DROP TABLE IF EXISTS {table}")
    cnt.close()

def get_first_row(table, row):
    # create connection to database
    cnt = sqlite3.connect('config.db')
    cnt.row_factory = sqlite3.Row
    cursor = cnt.execute(f"SELECT * FROM {table}")
    rows = cursor.fetchone()
    result = rows[row]
    cnt.close()
    return result

def get_all_rows(table):
    # create connection to database
    cnt = sqlite3.connect('config.db')
    cnt.row_factory = sqlite3.Row
    cursor = cnt.execute(f"SELECT * FROM {table}")
    result = cursor.fetchall()
    cnt.close()
    return result

def get_empty_tables():
    # create connection to database
    cnt = sqlite3.connect('config.db')
    empty_tables = []
    cnt.row_factory = sqlite3.Row
    tables = ["ACTIONS", "CONFIG", "DEFAULT_LENGTH", "DEFAULT_QUOTE", "AVERAGE_RATIO"]

    for table in tables:
        cursor = cnt.execute(f"SELECT * FROM {table}")
        rows = cursor.fetchone()
        if (rows == None or len(rows) == 0):
            empty_tables.append(table)

    cnt.close()
    return empty_tables
