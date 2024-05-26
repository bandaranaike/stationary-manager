import tkinter as tk
from tkinter import ttk, messagebox
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


def toggle_stock_details(event):
    item_id = item_tree.focus()
    item_data = item_tree.item(item_id)
    children = item_tree.get_children(item_id)

    if children:
        item_tree.delete(*children)
    else:
        stocks = fetch_stocks_by_item_id(conn, item_data['values'][0])
        for stock in stocks:
            item_tree.insert(item_id, "end", values=("", "", stock[1], stock[2], stock[3], stock[4]), tags=('stock',))


def open_add_item_popup():
    popup = tk.Toplevel(root)
    popup.title("Add Item")
    popup.geometry("300x250")

    helvetica_font = ("Helvetica", 12)

    tk.Label(popup, text="Item Code", font=helvetica_font).grid(row=0, column=0, padx=10, pady=5)
    entry_code = ttk.Entry(popup, font=helvetica_font)
    entry_code.grid(row=0, column=1, padx=10, pady=5)

    tk.Label(popup, text="Item Name", font=helvetica_font).grid(row=1, column=0, padx=10, pady=5)
    entry_name = ttk.Entry(popup, font=helvetica_font)
    entry_name.grid(row=1, column=1, padx=10, pady=5)

    tk.Label(popup, text="Full Value", font=helvetica_font).grid(row=2, column=0, padx=10, pady=5)
    entry_value = ttk.Entry(popup, font=helvetica_font)
    entry_value.grid(row=2, column=1, padx=10, pady=5)

    tk.Label(popup, text="Stock", font=helvetica_font).grid(row=3, column=0, padx=10, pady=5)
    entry_stock = ttk.Entry(popup, font=helvetica_font)
    entry_stock.grid(row=3, column=1, padx=10, pady=5)

    tk.Label(popup, text="Status", font=helvetica_font).grid(row=4, column=0, padx=10, pady=5)
    entry_status = ttk.Entry(popup, font=helvetica_font)
    entry_status.grid(row=4, column=1, padx=10, pady=5)

    def add_item():
        conn = create_connection("stationary_stock.db")
        cursor = conn.cursor()
        cursor.execute('''
        INSERT INTO item (code, name, full_value, stock, status)
        VALUES (?, ?, ?, ?, ?)
        ''', (entry_code.get(), entry_name.get(), float(entry_value.get()), int(entry_stock.get()), entry_status.get()))
        conn.commit()
        conn.close()
        messagebox.showinfo("Success", "Item added successfully")
        popup.destroy()
        refresh_item_list()

    ttk.Button(popup, text="Add Item", command=add_item).grid(row=5, column=1, pady=10)


def refresh_item_list():
    for i in item_tree.get_children():
        item_tree.delete(i)
    items = fetch_all_items(conn)
    for item in items:
        item_tree.insert("", "end", values=item)


def create_main_window():
    global conn, item_tree, root
    conn = create_connection("stationary_stock.db")

    root = tk.Tk()
    root.title("Stationary Stock Management")

    style = ttk.Style()
    style.theme_use("clam")
    helvetica_font = ("Helvetica", 12)
    style.configure("TButton", font=helvetica_font)
    style.configure("TLabel", font=helvetica_font)
    style.configure("Treeview.Heading", font=("Helvetica", 14, "bold"))
    style.configure("Treeview", font=helvetica_font)

    add_item_button = ttk.Button(root, text="Add Item", command=open_add_item_popup)
    add_item_button.pack(pady=10)

    item_tree = ttk.Treeview(root, columns=("ID", "Code", "Name", "Full Value", "Stock", "Status"), show='headings',
                             style="Treeview")

    item_tree.heading("ID", text="ID")
    item_tree.heading("Code", text="Code")
    item_tree.heading("Name", text="Name")
    item_tree.heading("Full Value", text="Full Value")
    item_tree.heading("Stock", text="Stock")
    item_tree.heading("Status", text="Status")

    refresh_item_list()

    item_tree.bind("<Double-1>", toggle_stock_details)
    item_tree.pack(expand=True, fill='both')

    root.mainloop()


if __name__ == "__main__":
    create_main_window()
