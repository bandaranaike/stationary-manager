import sqlite3


def update_item_status():
    conn = sqlite3.connect('stationary_stock.db')
    cursor = conn.cursor()

    cursor.execute('SELECT id, reorder_level FROM items')
    items = cursor.fetchall()

    for item_id, reorder_level in items:
        update_single_item_status(cursor, item_id, reorder_level)

    conn.commit()
    conn.close()


def update_single_item_status(cursor, item_id, reorder_level):
    # Correct SQL query to get total stock and total value
    cursor.execute('''
        SELECT 
            IFNULL(SUM(stock), 0) AS total_stock, 
            IFNULL(SUM(stock * unit_price), 0) AS total_value 
        FROM stocks 
        WHERE item_id = ?
    ''', (item_id,))

    # Fetch total stock and total value
    result = cursor.fetchone()
    total_stock = result[0]
    total_value = result[1]

    # Determine status based on total stock
    status = 'GOOD' if total_stock > reorder_level else 'ORDER'

    # Update the items table
    cursor.execute('''
        UPDATE items
        SET total_stock = ?, total_value = ?, status = ?
        WHERE id = ?
    ''', (total_stock, total_value, status, item_id))
