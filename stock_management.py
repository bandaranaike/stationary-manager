import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3

from files_and_path_generator import generate_pdf_filename
from generate_report import fetch_data, generate_pdf  # Import the required functions
from remove_empty_stocks import remove_empty_stocks  # Import the required functions


class StockManagement:
    def __init__(self, parent):
        self.stock_price_entry = None
        self.stock_quantity_entry = None
        self.item_combobox = None
        self.new_stock_window = None
        self.item_code_entry = None
        self.item_reorder_entry = None
        self.item_name_entry = None
        self.new_item_window = None
        self.generate_report_button = None
        self.add_stock_button = None
        self.add_item_button = None
        self.parent = parent
        self.create_widgets()
        self.db_path = 'stationary_stock.db'

    def create_widgets(self):
        self.stock_tree = ttk.Treeview(self.parent,
                                       columns=("id", "code", "name", "total_value", "total_stock", "status"),
                                       show="headings")
        self.stock_tree.heading("id", text="ID")
        self.stock_tree.heading("code", text="Code")
        self.stock_tree.heading("name", text="Name")
        self.stock_tree.heading("total_value", text="Total Value")
        self.stock_tree.heading("total_stock", text="Total Stock")
        self.stock_tree.heading("status", text="Status")

        self.stock_tree.bind('<Double-1>', self.expand_item)

        self.stock_tree.pack(fill=tk.BOTH, expand=True)

        self.populate_stock_tree()

        self.add_item_button = tk.Button(self.parent, text="Add New Item", command=self.add_new_item)
        self.add_item_button.pack(side=tk.LEFT, padx=10, pady=10)

        self.add_stock_button = tk.Button(self.parent, text="Add New Stock", command=self.add_new_stock)
        self.add_stock_button.pack(side=tk.LEFT, padx=10, pady=10)

        self.generate_report_button = tk.Button(self.parent, text="Remove empty stocks",
                                                command=self.remove_empty_stocks)
        self.generate_report_button.pack(side=tk.LEFT, padx=10, pady=10)

        self.generate_report_button = tk.Button(self.parent, text="Generate Report",
                                                command=self.generate_report)
        self.generate_report_button.pack(side=tk.LEFT, padx=10, pady=10)

        self.generate_report_button = tk.Button(self.parent, text="Refresh view",
                                                command=self.refresh_view)
        self.generate_report_button.pack(side=tk.LEFT, padx=10, pady=10)

    def populate_stock_tree(self):
        for i in self.stock_tree.get_children():
            self.stock_tree.delete(i)
        conn = sqlite3.connect('stationary_stock.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM items")
        rows = cursor.fetchall()
        for row in rows:
            self.stock_tree.insert("", tk.END, values=row)
        conn.close()

    def add_new_item(self):
        self.new_item_window = tk.Toplevel(self.parent)
        self.new_item_window.title("Add New Item")

        tk.Label(self.new_item_window, text="Name").grid(row=0, column=0, padx=10, pady=10)
        self.item_name_entry = tk.Entry(self.new_item_window)
        self.item_name_entry.grid(row=0, column=1, padx=10, pady=10)

        tk.Label(self.new_item_window, text="Code").grid(row=1, column=0, padx=10, pady=10)
        self.item_code_entry = tk.Entry(self.new_item_window)
        self.item_code_entry.grid(row=1, column=1, padx=10, pady=10)

        tk.Label(self.new_item_window, text="Reorder Level").grid(row=2, column=0, padx=10, pady=10)
        self.item_reorder_entry = tk.Entry(self.new_item_window)
        self.item_reorder_entry.grid(row=2, column=1, padx=10, pady=10)

        tk.Button(self.new_item_window, text="Save", command=self.save_new_item).grid(row=3, column=0, columnspan=2,
                                                                                      pady=10)

    def save_new_item(self):
        name = self.item_name_entry.get()
        code = self.item_code_entry.get()
        reorder_level = self.item_reorder_entry.get()
        if name and code:
            conn = sqlite3.connect('stationary_stock.db')
            cursor = conn.cursor()
            cursor.execute("INSERT INTO items (name, code, reorder_level) VALUES (?, ?, ?)",
                           (name, code, reorder_level))
            conn.commit()
            conn.close()
            self.new_item_window.destroy()
            self.populate_stock_tree()
        else:
            messagebox.showwarning("Input Error", "Please enter both name and code.")

    def refresh_view(self):
        if self.new_stock_window:
            self.new_item_window.destroy()
        if self.new_stock_window:
            self.new_stock_window.destroy()
        self.populate_stock_tree()

    def add_new_stock(self):
        self.new_stock_window = tk.Toplevel(self.parent)
        self.new_stock_window.title("Add New Stock")

        tk.Label(self.new_stock_window, text="Item").grid(row=0, column=0, padx=10, pady=10)
        self.item_combobox = ttk.Combobox(self.new_stock_window)
        self.item_combobox.grid(row=0, column=1, padx=10, pady=10)
        self.populate_item_combobox()

        tk.Label(self.new_stock_window, text="Quantity").grid(row=1, column=0, padx=10, pady=10)
        self.stock_quantity_entry = tk.Entry(self.new_stock_window)
        self.stock_quantity_entry.grid(row=1, column=1, padx=10, pady=10)

        tk.Label(self.new_stock_window, text="Unit Price").grid(row=2, column=0, padx=10, pady=10)
        self.stock_price_entry = tk.Entry(self.new_stock_window)
        self.stock_price_entry.grid(row=2, column=1, padx=10, pady=10)

        tk.Button(self.new_stock_window, text="Save", command=self.save_new_stock).grid(row=3, column=0, columnspan=2,
                                                                                        pady=10)

    def populate_item_combobox(self):
        conn = sqlite3.connect('stationary_stock.db')
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, code FROM items")
        rows = cursor.fetchall()
        items = ["{} - {} - {}".format(row[0], row[1], row[2]) for row in rows]

        self.item_combobox['values'] = items
        conn.close()

    def save_new_stock(self):
        item = self.item_combobox.get()
        quantity = self.stock_quantity_entry.get()
        price = self.stock_price_entry.get()

        if item and quantity and price:
            item_id = item.split(" - ")[0]
            conn = sqlite3.connect('stationary_stock.db')
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO stocks (item_id, date, unit_price, stock, initial_stock) VALUES (?, DATE('now'), ?, ?, ?)",
                (item_id, price, quantity, quantity))
            cursor.execute("UPDATE items SET total_value = total_value + ?, total_stock = total_stock + ? WHERE id = ?",
                           (float(price) * int(quantity), int(quantity), item_id))
            conn.commit()
            conn.close()
            self.new_stock_window.destroy()
            self.populate_stock_tree()
        else:
            messagebox.showwarning("Input Error", "Please fill all fields.")

    def expand_item(self, event):
        selected_item = self.stock_tree.selection()[0]
        item_id = self.stock_tree.item(selected_item, 'values')[0]

        if not self.stock_tree.get_children(selected_item):
            conn = sqlite3.connect('stationary_stock.db')
            cursor = conn.cursor()
            stocks = cursor.execute(
                "SELECT '', date, unit_price, stock, initial_stock, unit_price * stock AS t_value FROM stocks WHERE item_id=?",
                (item_id,))

            # Insert column headers as a child item
            self.stock_tree.insert(selected_item, 'end',
                                   values=("", "Date", "Unit Price", "Stock", "Initial Stock", "Value"), open=True,
                                   tags='details_header')

            for stock in stocks:
                self.stock_tree.insert(selected_item, 'end', values=stock, tags='details')

            conn.close()

        # Style the separator
        background_color = '#E9E9E9'
        self.stock_tree.tag_configure('details', foreground='#37403F', background=background_color)
        self.stock_tree.tag_configure('details_header', foreground='#292929', background=background_color)

    def generate_report(self):
        pdf_path = generate_pdf_filename('reports')

        try:
            data, total_sum = fetch_data(self.db_path)
            generate_pdf(data, total_sum, pdf_path)
            messagebox.showinfo("Report", "Report generated successfully.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate report: {e}")

    def remove_empty_stocks(self):
        try:
            remove_empty_stocks(self.db_path)
            messagebox.showinfo("Report", "Empty stock has been removed.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to remove empty stocks: {e}")


if __name__ == "__main__":
    root = tk.Tk()
    app = StockManagement(root)
    root.mainloop()
