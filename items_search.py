import tkinter as tk
from tkinter import ttk
import sqlite3


def fetch_items():
    conn = sqlite3.connect('stationary_stock.db')
    cursor = conn.cursor()
    cursor.execute("SELECT id, name FROM item")
    items = [f"{row[0]} - {row[1]}" for row in cursor.fetchall()]
    conn.close()
    return items


def update_combobox(event):
    # Get the typed value
    typed = combobox_item_id.get()

    # Fetch items from database
    items = fetch_items()

    # Filter items based on typed value
    filtered_items = [item for item in items if typed.lower() in item.lower()]

    # Update combobox values
    combobox_item_id['values'] = filtered_items

    # Show the dropdown list
    if filtered_items:
        combobox_item_id.event_generate('<Down>')


root = tk.Tk()
root.title("Bank Stationary Management")

# Label for Item ID
tk.Label(root, text="Item ID").grid(row=6, column=0)

# Combobox for Item ID
combobox_item_id = ttk.Combobox(root)
combobox_item_id.grid(row=6, column=1)

# Fetch initial items from database
items = fetch_items()
combobox_item_id['values'] = items

# Bind the key release event to the update_combobox function
combobox_item_id.bind('<KeyRelease>', update_combobox)

root.mainloop()
