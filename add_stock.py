import tkinter as tk
from tkinter import messagebox
import sqlite3
from datetime import date


# Connect to SQLite database
def connect_db():
    return sqlite3.connect('stationary_stock.db')


# Add a new stock entry
def add_stock():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('''
    INSERT INTO stock (item_id, date, unit_price, quantity, stock)
    VALUES (?, ?, ?, ?, ?)
    ''', (int(entry_item_id.get()), str(date.today()), float(entry_unit_price.get()), int(entry_quantity.get()),
          int(entry_stock_quantity.get())))
    conn.commit()
    conn.close()
    messagebox.showinfo("Success", "Stock entry added successfully")


# GUI Setup
root = tk.Tk()

# Stock Entry Form
tk.Label(root, text="Item ID").grid(row=6, column=0)
entry_item_id = tk.Entry(root)
entry_item_id.grid(row=6, column=1)

tk.Label(root, text="Unit Price").grid(row=7, column=0)
entry_unit_price = tk.Entry(root)
entry_unit_price.grid(row=7, column=1)

tk.Label(root, text="Quantity").grid(row=8, column=0)
entry_quantity = tk.Entry(root)
entry_quantity.grid(row=8, column=1)

tk.Label(root, text="Stock Quantity").grid(row=9, column=0)
entry_stock_quantity = tk.Entry(root)
entry_stock_quantity.grid(row=9, column=1)

tk.Button(root, text="Add Stock Entry", command=add_stock).grid(row=10, column=1)

root.mainloop()
