import sqlite3


def create_tables():
    connection = sqlite3.connect('stationary_stock.db')
    cursor = connection.cursor()

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        code TEXT NOT NULL,
        name TEXT NOT NULL,
        total_value REAL DEFAULT 0,
        total_stock INTEGER DEFAULT 0,
        status TEXT DEFAULT 'active'
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS stocks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        item_id INTEGER NOT NULL,
        date TEXT NOT NULL,
        unit_price REAL NOT NULL,
        stock INTEGER NOT NULL,
        initial_stock INTEGER NOT NULL,
        FOREIGN KEY (item_id) REFERENCES items(id)
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS branches (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        code TEXT NOT NULL,
        account_number TEXT NOT NULL
    )
    ''')

    connection.commit()
    connection.close()


if __name__ == "__main__":
    create_tables()
    print("Database and tables created successfully.")
