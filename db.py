import sqlite3

def create_tables():
    # create connection to database
    cnt = sqlite3.connect('config.db')

    # Create a CONFIG TABLE
    cnt.execute('''CREATE TABLE IF NOT EXISTS CONFIG(
    update_config INTEGER,
    create_actions INTEGER,
    load_new_quote INTEGER,
    instant_start_timers INTEGER,
    change_default_quote INTEGER,
    default_timers_based_on_round_average INTEGER,
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

def insert_default_values():
    # create connection to database
    cnt = sqlite3.connect('config.db')
    cnt.execute('''INSERT INTO CONFIG VALUES(0,0,1,0,0,0,0)''')
    cnt.execute('''INSERT INTO ACTIONS VALUES('Meditate'),('Jumping Jacks'),('Pushups'),('Squats'),('Walk the dogs'),('Read a book'),('Go outside')''')
    cnt.execute('''INSERT INTO AVERAGE_RATIO VALUES(25,1,5,1)''')
    cnt.execute('''INSERT INTO DEFAULT_LENGTH VALUES(25,5)''')
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

def drop_table(table):
    # create connection to database
    cnt = sqlite3.connect('config.db')
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

def get_row(table, row):
    # create connection to database
    cnt = sqlite3.connect('config.db')
    cnt.row_factory = sqlite3.Row
    cursor = cnt.execute(f"SELECT {row} FROM {table}")
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

def update_table(table, row, value):
    # create connection to database
    cnt = sqlite3.connect('config.db')

    cnt.execute(f"UPDATE {table} SET {row} = '{value}'")
    cnt.commit()
    cnt.close()

create_tables()
insert_default_values()
