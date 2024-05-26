import tkinter as tk
from tkinter import messagebox
import sqlite3


# Connect to SQLite database
def connect_db():
    return sqlite3.connect('stationary_stock.db')


# Add a new item to the database
def add_item():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('''
    INSERT INTO item (code, name, full_value, stock, status)
    VALUES (?, ?, ?, ?, ?)
    ''', (entry_code.get(), entry_name.get(), float(entry_value.get()), int(entry_stock.get()), entry_status.get()))
    conn.commit()
    conn.close()
    messagebox.showinfo("Success", "Item added successfully")


# Add a new stock entry

# GUI Setup
root = tk.Tk()
root.title("Bank Stationary Stock Management")

# Item Entry Form
tk.Label(root, text="Item Code").grid(row=0, column=0)
entry_code = tk.Entry(root)
entry_code.grid(row=0, column=1)

tk.Label(root, text="Item Name").grid(row=1, column=0)
entry_name = tk.Entry(root)
entry_name.grid(row=1, column=1)

tk.Label(root, text="Full Value").grid(row=2, column=0)
entry_value = tk.Entry(root)
entry_value.grid(row=2, column=1)

tk.Label(root, text="Stock").grid(row=3, column=0)
entry_stock = tk.Entry(root)
entry_stock.grid(row=3, column=1)

tk.Label(root, text="Status").grid(row=4, column=0)
entry_status = tk.Entry(root)
entry_status.grid(row=4, column=1)

tk.Button(root, text="Add Item", command=add_item).grid(row=5, column=1)

# Stock Entry Form
root.mainloop()
