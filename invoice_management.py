import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3


class InvoiceManagement:
    def __init__(self, parent):
        self.parent = parent
        self.create_widgets()

    def create_widgets(self):
        self.invoice_frame = ttk.Frame(self.parent)
        self.invoice_frame.pack(expand=1, fill="both")

        self.invoice_tree = ttk.Treeview(self.invoice_frame, columns=("item", "quantity", "unit_price", "total_value"),
                                         show="headings")
        self.invoice_tree.heading("item", text="Item")
        self.invoice_tree.heading("quantity", text="Quantity")
        self.invoice_tree.heading("unit_price", text="Unit Price")
        self.invoice_tree.heading("total_value", text="Total Value")

        self.invoice_tree.pack(fill=tk.BOTH, expand=1)

        self.add_item_button = tk.Button(self.invoice_frame, text="Add Item to Invoice", command=self.add_invoice_item)
        self.add_item_button.pack(side=tk.LEFT, padx=10, pady=10)

        self.save_invoice_button = tk.Button(self.invoice_frame, text="Save Invoice", command=self.save_invoice)
        self.save_invoice_button.pack(side=tk.LEFT, padx=10, pady=10)

    def add_invoice_item(self):
        self.new_invoice_item_window = tk.Toplevel(self.parent)
        self.new_invoice_item_window.title("Add Item to Invoice")

        tk.Label(self.new_invoice_item_window, text="Item").grid(row=0, column=0, padx=10, pady=10)
        self.item_combobox = ttk.Combobox(self.new_invoice_item_window)
        self.item_combobox.grid(row=0, column=1, padx=10, pady=10)
        self.populate_item_combobox()

        tk.Label(self.new_invoice_item_window, text="Quantity").grid(row=1, column=0, padx=10, pady=10)
        self.item_quantity_entry = tk.Entry(self.new_invoice_item_window)
        self.item_quantity_entry.grid(row=1, column=1, padx=10, pady=10)

        tk.Label(self.new_invoice_item_window, text="Unit Price").grid(row=2, column=0, padx=10, pady=10)
        self.item_price_entry = tk.Entry(self.new_invoice_item_window)
        self.item_price_entry.grid(row=2, column=1, padx=10, pady=10)

        tk.Button(self.new_invoice_item_window, text="Add", command=self.save_invoice_item).grid(row=3, column=0,
                                                                                                 columnspan=2, pady=10)

    def populate_item_combobox(self):
        conn = sqlite3.connect('stationary_stock.db')
        cursor = conn.cursor()
        cursor.execute("SELECT id, name FROM items")
        rows = cursor.fetchall()
        items = ["{} - {}".format(row[0], row[1]) for row in rows]
        self.item_combobox['values'] = items
        conn.close()

    def save_invoice_item(self):
        item = self.item_combobox.get()
        quantity = self.item_quantity_entry.get()
        price = self.item_price_entry.get()

        if item and quantity and price:
            item_name = item.split(" - ")[1]
            total_value = float(price) * int(quantity)
            self.invoice_tree.insert("", tk.END, values=(item_name, quantity, price, total_value))
            self.new_invoice_item_window.destroy()
        else:
            messagebox.showwarning("Input Error", "Please fill all fields.")

    def save_invoice(self):
        # Implement saving invoice to database and generating PDF
        pass


if __name__ == "__main__":
    root = tk.Tk()
    app = InvoiceManagement(root)
    root.mainloop()
