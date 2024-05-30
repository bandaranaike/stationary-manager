import tkinter as tk
from tkinter import ttk, messagebox
from db_utils import create_connection, fetch_all_items, fetch_stocks_by_item_id, fetch_items
from datetime import date


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


def update_combobox(event):
    typed = combobox_item_id.get()
    items = fetch_items(typed)
    filtered_items = [item for item in items if typed.lower() in item.lower()]
    combobox_item_id['values'] = filtered_items
    if filtered_items:
        combobox_item_id.event_generate('<Down>')


def open_add_stock_popup():
    popup = tk.Toplevel(root)
    popup.title("Add Stock")
    popup.geometry("400x300")
    helvetica_font = ("Helvetica", 12)
    tk.Label(popup, text="Item ID", font=helvetica_font).grid(row=0, column=0, padx=10, pady=5)
    global combobox_item_id
    combobox_item_id = ttk.Combobox(popup, font=helvetica_font)
    combobox_item_id.grid(row=0, column=1, padx=10, pady=5)
    items = fetch_items('')
    combobox_item_id['values'] = items
    combobox_item_id.bind('<KeyRelease>', update_combobox)
    tk.Label(popup, text="Unit Price", font=helvetica_font).grid(row=1, column=0, padx=10, pady=5)
    entry_unit_price = ttk.Entry(popup, font=helvetica_font)
    entry_unit_price.grid(row=1, column=1, padx=10, pady=5)
    tk.Label(popup, text="Quantity", font=helvetica_font).grid(row=2, column=0, padx=10, pady=5)
    entry_quantity = ttk.Entry(popup, font=helvetica_font)
    entry_quantity.grid(row=2, column=1, padx=10, pady=5)
    tk.Label(popup, text="Stock Quantity", font=helvetica_font).grid(row=3, column=0, padx=10, pady=5)
    entry_stock_quantity = ttk.Entry(popup, font=helvetica_font)
    entry_stock_quantity.grid(row=3, column=1, padx=10, pady=5)

    def add_stock():
        conn = create_connection("stationary_stock.db")
        cursor = conn.cursor()
        item_id = combobox_item_id.get().split(" - ")[0]  # Extract item ID from combobox selection
        cursor.execute('''
        INSERT INTO stock (item_id, date, unit_price, quantity, stock)
        VALUES (?, ?, ?, ?, ?)
        ''', (int(item_id), str(date.today()), float(entry_unit_price.get()), int(entry_quantity.get()),
              int(entry_stock_quantity.get())))
        conn.commit()
        conn.close()
        messagebox.showinfo("Success", "Stock entry added successfully")
        popup.destroy()

    ttk.Button(popup, text="Add Stock Entry", command=add_stock).grid(row=4, column=1, pady=10)


def refresh_item_list():
    for i in item_tree.get_children():
        item_tree.delete(i)
    items = fetch_all_items(conn)
    for item in items:
        item_tree.insert("", "end", values=item)


def create_stock_management_tab(tab_frame):
    global conn, item_tree, root
    conn = create_connection("stationary_stock.db")
    root = tab_frame

    style = ttk.Style()
    style.theme_use("clam")
    helvetica_font = ("Helvetica", 12)
    style.configure("TButton", font=helvetica_font)
    style.configure("TLabel", font=helvetica_font)
    style.configure("Treeview.Heading", font=("Helvetica", 14, "bold"))
    style.configure("Treeview", font=helvetica_font)

    add_item_button = ttk.Button(tab_frame, text="Add Item", command=open_add_item_popup)
    add_item_button.pack(pady=10)

    add_stock_button = ttk.Button(tab_frame, text="Add Stock", command=open_add_stock_popup)
    add_stock_button.pack(pady=10)

    item_tree = ttk.Treeview(tab_frame, columns=("ID", "Code", "Name", "Full Value", "Stock", "Status"),
                             show='headings', style="Treeview")
    item_tree.heading("ID", text="ID")
    item_tree.heading("Code", text="Code")
    item_tree.heading("Name", text="Name")
    item_tree.heading("Full Value", text="Full Value")
    item_tree.heading("Stock", text="Stock")
    item_tree.heading("Status", text="Status")

    refresh_item_list()
    item_tree.bind("<Double-1>", toggle_stock_details)
    item_tree.pack(expand=True, fill='both')
