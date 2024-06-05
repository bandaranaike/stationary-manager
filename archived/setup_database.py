import sqlite3


def create_tables():
    conn = sqlite3.connect('stationary_stock.db')
    cursor = conn.cursor()

    cursor.execute('''CREATE TABLE IF NOT EXISTS items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        code TEXT NOT NULL,
        name TEXT NOT NULL,
        total_value REAL NOT NULL,
        total_stock INTEGER NOT NULL,
        status TEXT NOT NULL
    )''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS stocks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        item_id INTEGER,
        date DATE NOT NULL,
        unit_price REAL NOT NULL,
        stock INTEGER NOT NULL,
        initial_stock INTEGER NOT NULL,
        FOREIGN KEY (item_id) REFERENCES items(id)
    )''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS branches (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        code TEXT NOT NULL,
        account_number TEXT NOT NULL
    )''')

    conn.commit()
    conn.close()


if __name__ == '__main__':
    create_tables()
