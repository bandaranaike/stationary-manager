import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import date


# Database Connection and Queries
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


def fetch_items():
    conn = create_connection('stationary_stock.db')
    cursor = conn.cursor()
    query = combobox_item_id.get()
    cursor.execute("SELECT id, name, code FROM item WHERE name LIKE ? OR code LIKE ?",
                   ('%' + query + '%', '%' + query + '%'))
    items = [f"{row[0]} - {row[1]}" for row in cursor.fetchall()]
    conn.close()
    return items


# Functions for the Stock Management Tab
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
    items = fetch_items()
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
    items = fetch_items()
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


# Invoice Tab Class
class InvoiceApp:
    def __init__(self, root):
        self.root = root

        # Connect to the database
        self.conn = sqlite3.connect('stationary_stock.db')
        self.cursor = self.conn.cursor()

        # Fetch all items for the combobox
        self.cursor.execute('SELECT code, name FROM item')
        items = self.cursor.fetchall()
        self.item_dict = {f"{code} - {name}": (code, name) for code, name in items}
        self.item_list = list(self.item_dict.keys())

        # Frame for adding items
        self.add_frame = tk.Frame(self.root)
        self.add_frame.pack(pady=10)

        # Combobox for item search
        self.item_label = tk.Label(self.add_frame, text="Item:")
        self.item_label.grid(row=0, column=0)
        self.item_combobox = ttk.Combobox(self.add_frame, values=self.item_list)
        self.item_combobox.grid(row=0, column=1, padx=10)
        self.item_combobox.bind('<KeyRelease>', self.autocomplete)
        self.item_combobox.bind('<<ComboboxSelected>>', self.update_price_and_total)

        # Unit price label
        self.unit_price_label = tk.Label(self.add_frame, text="Unit Price:")
        self.unit_price_label.grid(row=0, column=2)
        self.unit_price_var = tk.StringVar()
        self.unit_price_entry = tk.Entry(self.add_frame, textvariable=self.unit_price_var, state='readonly')
        self.unit_price_entry.grid(row=0, column=3, padx=10)

        # Quantity entry
        self.quantity_label = tk.Label(self.add_frame, text="Quantity:")
        self.quantity_label.grid(row=0, column=4)
        self.quantity_var = tk.StringVar()
        self.quantity_entry = tk.Entry(self.add_frame, textvariable=self.quantity_var)
        self.quantity_entry.grid(row=0, column=5, padx=10)
        self.quantity_entry.bind('<KeyRelease>', self.update_price_and_total)

        # Total value label
        self.total_value_label = tk.Label(self.add_frame, text="Total Value:")
        self.total_value_label.grid(row=0, column=6)
        self.total_value_var = tk.StringVar()
        self.total_value_entry = tk.Entry(self.add_frame, textvariable=self.total_value_var, state='readonly')
        self.total_value_entry.grid(row=0, column=7, padx=10)

        # Add button
        self.add_button = tk.Button(self.add_frame, text="Add", command=self.add_item)
        self.add_button.grid(row=0, column=8, padx=10)

        # Treeview for invoice
        self.invoice_tree = ttk.Treeview(self.root, columns=("item", "unit_price", "quantity", "total_value"),
                                         show='headings')
        self.invoice_tree.heading("item", text="Item")
        self.invoice_tree.heading("unit_price", text="Unit Price")
        self.invoice_tree.heading("quantity", text="Quantity")
        self.invoice_tree.heading("total_value", text="Total Value")
        self.invoice_tree.pack(pady=10)

        # Button to remove selected item
        self.remove_button = tk.Button(self.root, text="Remove", command=self.remove_item)
        self.remove_button.pack(pady=5)

        # Save button
        self.save_button = tk.Button(self.root, text="Save", command=self.save_invoice)
        self.save_button.pack(pady=5)

        # Total value label at the bottom
        self.total_invoice_value_label = tk.Label(self.root, text="Total Invoice Value: 0.00")
        self.total_invoice_value_label.pack(pady=10)

        # Temporary storage for stock levels
        self.temp_stock_levels = {}

    def autocomplete(self, event):
        value = event.widget.get()
        if value == '':
            self.item_combobox['values'] = self.item_list
        else:
            data = []
            for item in self.item_list:
                if value.lower() in item.lower():
                    data.append(item)
            self.item_combobox['values'] = data

    def update_price_and_total(self, event):
        selected_item = self.item_combobox.get()
        if selected_item and selected_item in self.item_dict:
            code, name = self.item_dict[selected_item]

            # Fetch the item ID
            self.cursor.execute('SELECT id FROM item WHERE code = ?', (code,))
            item_id = self.cursor.fetchone()[0]
            # Fetch the stocks in the order of the oldest first
            self.cursor.execute('SELECT unit_price, stock FROM stock WHERE item_id = ? ORDER BY date', (item_id,))
            stocks = self.cursor.fetchall()

            try:
                quantity_needed = int(self.quantity_var.get())
                if quantity_needed <= 0:
                    raise ValueError("Quantity must be positive")

                total_price = 0
                remaining_quantity = quantity_needed

                for unit_price, stock_quantity in stocks:
                    if remaining_quantity <= 0:
                        break
                    if stock_quantity >= remaining_quantity:
                        total_price += remaining_quantity * unit_price
                        remaining_quantity = 0
                    else:
                        total_price += stock_quantity * unit_price
                        remaining_quantity -= stock_quantity

                if remaining_quantity > 0:
                    messagebox.showwarning("Stock Error", "Not enough stock available")
                    self.unit_price_var.set("0.00")
                    self.total_value_var.set("0.00")
                else:
                    self.unit_price_var.set(f"{total_price / quantity_needed:.2f}")
                    self.total_value_var.set(f"{total_price:.2f}")

            except ValueError:
                self.unit_price_var.set("0.00")
                self.total_value_var.set("0.00")

    def add_item(self):
        selected_item = self.item_combobox.get()
        quantity = self.quantity_var.get()
        if selected_item and selected_item in self.item_dict and quantity:
            code, name = self.item_dict[selected_item]
            try:
                quantity = int(quantity)
                if quantity <= 0:
                    raise ValueError("Quantity must be positive")

                self.cursor.execute('SELECT id FROM item WHERE code = ?', (code,))
                item_id = self.cursor.fetchone()[0]

                self.cursor.execute('SELECT id, unit_price, stock FROM stock WHERE item_id = ? ORDER BY date',
                                    (item_id,))
                stocks = self.cursor.fetchall()

                if item_id not in self.temp_stock_levels:
                    self.temp_stock_levels[item_id] = []
                    for stock_id, unit_price, stock_quantity in stocks:
                        self.temp_stock_levels[item_id].append([stock_id, unit_price, stock_quantity])

                remaining_quantity = quantity
                rows_to_add = []
                for stock in self.temp_stock_levels[item_id]:
                    stock_id, unit_price, stock_quantity = stock
                    if remaining_quantity <= 0:
                        break
                    if stock_quantity >= remaining_quantity:
                        rows_to_add.append((f"{code} - {name}", f"{unit_price:.2f}", remaining_quantity,
                                            f"{remaining_quantity * unit_price:.2f}"))
                        stock[2] -= remaining_quantity
                        remaining_quantity = 0
                    else:
                        rows_to_add.append((f"{code} - {name}", f"{unit_price:.2f}", stock_quantity,
                                            f"{stock_quantity * unit_price:.2f}"))
                        remaining_quantity -= stock_quantity
                        stock[2] = 0

                if remaining_quantity > 0:
                    messagebox.showwarning("Stock Error", "Not enough stock available")
                else:
                    for row in rows_to_add:
                        if int(row[2]) > 0:  # Only add rows with quantity greater than 0
                            self.invoice_tree.insert("", 0, values=row)

                    self.update_total_invoice_value()
                    self.item_combobox.set('')
                    self.unit_price_var.set('')
                    self.quantity_var.set('')
                    self.total_value_var.set('')

            except ValueError:
                messagebox.showwarning("Input Error", "Please enter a valid quantity")
        else:
            messagebox.showwarning("Input Error", "Please select an item and enter quantity")

    def remove_item(self):
        selected_items = self.invoice_tree.selection()

        if selected_items:
            for selected_item in selected_items:
                item_data = self.invoice_tree.item(selected_item)['values']
                item_code, quantity = item_data[0].split(" - ")[0], int(item_data[2])

                # Fetch the item ID
                self.cursor.execute('SELECT id FROM item WHERE code = ?', (item_code,))
                item_id = self.cursor.fetchone()[0]

                # Restore the quantity to temporary storage
                if item_id in self.temp_stock_levels:
                    remaining_quantity = quantity
                    for stock in self.temp_stock_levels[item_id]:
                        stock_id, unit_price, stock_quantity = stock
                        stock[2] += remaining_quantity
                        remaining_quantity = 0

                self.invoice_tree.delete(selected_item)

            self.update_total_invoice_value()
        else:
            messagebox.showwarning("Selection Error", "Please select items to remove")

    def save_invoice(self):
        try:
            for item_id, stocks in self.temp_stock_levels.items():
                for stock in stocks:
                    stock_id, unit_price, stock_quantity = stock
                    self.cursor.execute('UPDATE stock SET stock = ? WHERE id = ?', (stock_quantity, stock_id))
            self.conn.commit()
            messagebox.showinfo("Success", "Invoice saved successfully")
            self.temp_stock_levels.clear()
            self.invoice_tree.delete(*self.invoice_tree.get_children())
            self.update_total_invoice_value()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save invoice: {e}")

    def update_total_invoice_value(self):
        total_value = 0.00
        for row_id in self.invoice_tree.get_children():
            row_data = self.invoice_tree.item(row_id)['values']
            total_value += float(row_data[3])
        self.total_invoice_value_label.config(text=f"Total Invoice Value: {total_value:.2f}")

    def __del__(self):
        # Close the database connection when the object is deleted
        self.conn.close()


# Main Application Window
def create_main_window():
    global conn, item_tree, root, notebook
    conn = create_connection("stationary_stock.db")

    root = tk.Tk()
    root.title("Stationary Stock Management")

    notebook = ttk.Notebook(root)
    notebook.pack(expand=True, fill='both')

    # Stock Management Tab
    stock_frame = tk.Frame(notebook)
    notebook.add(stock_frame, text="Stock Management")

    style = ttk.Style()
    style.theme_use("clam")
    helvetica_font = ("Helvetica", 12)
    style.configure("TButton", font=helvetica_font)
    style.configure("TLabel", font=helvetica_font)
    style.configure("Treeview.Heading", font=("Helvetica", 14, "bold"))
    style.configure("Treeview", font=helvetica_font)

    add_item_button = ttk.Button(stock_frame, text="Add Item", command=open_add_item_popup)
    add_item_button.pack(pady=10)

    add_stock_button = ttk.Button(stock_frame, text="Add Stock", command=open_add_stock_popup)
    add_stock_button.pack(pady=10)

    item_tree = ttk.Treeview(stock_frame, columns=("ID", "Code", "Name", "Full Value", "Stock", "Status"),
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

    # Invoice Tab
    invoice_frame = tk.Frame(notebook)
    notebook.add(invoice_frame, text="Invoice")

    InvoiceApp(invoice_frame)

    root.mainloop()


if __name__ == "__main__":
    create_main_window()
