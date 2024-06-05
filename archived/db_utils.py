import sqlite3


def create_connection(db_file):
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except sqlite3.Error as e:
        print(e)
    return conn


def fetch_all_items(conn):
    cur = conn.cursor()
    cur.execute("SELECT * FROM item")
    rows = cur.fetchall()
    return rows


def fetch_stocks_by_item_id(conn, item_id):
    cur = conn.cursor()
    cur.execute("SELECT * FROM stock WHERE item_id=?", (item_id,))
    rows = cur.fetchall()
    return rows


def fetch_items(query):
    conn = create_connection('stationary_stock.db')
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, code FROM item WHERE name LIKE ? OR code LIKE ?",
                   ('%' + query + '%', '%' + query + '%'))
    items = [f"{row[0]} - {row[1]}" for row in cursor.fetchall()]
    conn.close()
    return items
