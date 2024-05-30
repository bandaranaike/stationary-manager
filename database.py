import sqlite3

# Connect to SQLite database
conn = sqlite3.connect('stationary_stock.db')
cursor = conn.cursor()

# Create item table
cursor.execute('''
CREATE TABLE IF NOT EXISTS item (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    code TEXT NOT NULL,
    name TEXT NOT NULL,
    full_value REAL NOT NULL,
    stock INTEGER NOT NULL,
    status TEXT NOT NULL
)
''')

# Create stock table
cursor.execute('''
CREATE TABLE IF NOT EXISTS stock (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    item_id INTEGER,
    date TEXT NOT NULL,
    unit_price REAL NOT NULL,
    initial_stock INTEGER NOT NULL,
    stock INTEGER NOT NULL,
    FOREIGN KEY (item_id) REFERENCES item(id)
)
''')

conn.commit()
conn.close()
