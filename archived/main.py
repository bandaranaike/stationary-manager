import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from tkcalendar import DateEntry
from fpdf import FPDF


class StationaryStockManager(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("BOC COP Stationary Stock Manager")
        self.geometry("800x600")

        self.notebook = ttk.Notebook(self)
        self.notebook.pack(expand=True, fill='both')

        self.create_stationary_list_tab()
        self.create_invoice_tab()

    def create_stationary_list_tab(self):
        self.stationary_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.stationary_frame, text="Stationary List")

        self.stationary_tree = ttk.Treeview(self.stationary_frame,
                                            columns=("Code", "Name", "Total Stock", "Total Value", "Status"),
                                            show='headings')
        self.stationary_tree.heading("Code", text="Code")
        self.stationary_tree.heading("Name", text="Name")
        self.stationary_tree.heading("Total Stock", text="Total Stock")
        self.stationary_tree.heading("Total Value", text="Total Value")
        self.stationary_tree.heading("Status", text="Status")
        self.stationary_tree.pack(expand=True, fill='both')

        self.load_items()

        self.add_item_button = ttk.Button(self.stationary_frame, text="Add Item", command=self.add_item)
        self.add_item_button.pack(side='left')

        self.add_stock_button = ttk.Button(self.stationary_frame, text="Add Stock", command=self.add_stock)
        self.add_stock_button.pack(side='left')

    def create_invoice_tab(self):
        self.invoice_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.invoice_frame, text="Invoice")

        self.invoice_tree = ttk.Treeview(self.invoice_frame, columns=("Code", "Name", "Qty", "Price", "Cost"),
                                         show='headings')
        self.invoice_tree.heading("Code", text="Code")
        self.invoice_tree.heading("Name", text="Name")
        self.invoice_tree.heading("Qty", text="Qty")
        self.invoice_tree.heading("Price", text="Price")
        self.invoice_tree.heading("Cost", text="Cost")
        self.invoice_tree.pack(expand=True, fill='both')

        self.save_invoice_button = ttk.Button(self.invoice_frame, text="Save Invoice", command=self.save_invoice)
        self.save_invoice_button.pack(side='bottom')

    def load_items(self):
        conn = sqlite3.connect('stationary_stock.db')
        cursor = conn.cursor()
        cursor.execute("SELECT code, name, total_stock, total_value, status FROM items")
        rows = cursor.fetchall()
        for row in rows:
            self.stationary_tree.insert('', tk.END, values=row)
        conn.close()

    def add_item(self):
        self.add_item_window = tk.Toplevel(self)
        self.add_item_window.title("Add Item")
        self.add_item_window.geometry("300x200")

        tk.Label(self.add_item_window, text="Name:").pack()
        self.item_name_entry = tk.Entry(self.add_item_window)
        self.item_name_entry.pack()

        tk.Label(self.add_item_window, text="Code:").pack()
        self.item_code_entry = tk.Entry(self.add_item_window)
        self.item_code_entry.pack()

        self.add_item_confirm_button = ttk.Button(self.add_item_window, text="Add", command=self.add_item_to_db)
        self.add_item_confirm_button.pack()

    def add_item_to_db(self):
        name = self.item_name_entry.get()
        code = self.item_code_entry.get()

        if not name or not code:
            messagebox.showerror("Error", "All fields are required")
            return

        conn = sqlite3.connect('stationary_stock.db')
        cursor = conn.cursor()
        cursor.execute("INSERT INTO items (name, code, total_value, total_stock, status) VALUES (?, ?, ?, ?, ?)",
                       (name, code, 0, 0, "Available"))
        conn.commit()
        conn.close()

        self.add_item_window.destroy()
        self.load_items()

    def add_stock(self):
        self.add_stock_window = tk.Toplevel(self)
        self.add_stock_window.title("Add Stock")
        self.add_stock_window.geometry("300x300")

        tk.Label(self.add_stock_window, text="Item:").pack()
        self.item_combobox = ttk.Combobox(self.add_stock_window)
        self.item_combobox.pack()

        tk.Label(self.add_stock_window, text="Unit Price:").pack()
        self.unit_price_entry = tk.Entry(self.add_stock_window)
        self.unit_price_entry.pack()

        tk.Label(self.add_stock_window, text="Quantity:").pack()
        self.quantity_entry = tk.Entry(self.add_stock_window)
        self.quantity_entry.pack()

        tk.Label(self.add_stock_window, text="Date:").pack()
        self.date_entry = DateEntry(self.add_stock_window)
        self.date_entry.pack()

        self.add_stock_confirm_button = ttk.Button(self.add_stock_window, text="Add", command=self.add_stock_to_db)
        self.add_stock_confirm_button.pack()

        self.load_item_combobox()

    def load_item_combobox(self):
        conn = sqlite3.connect('stationary_stock.db')
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM items")
        items = cursor.fetchall()
        item_list = [item[0] for item in items]
        self.item_combobox['values'] = item_list
        conn.close()

    def add_stock_to_db(self):
        item_name = self.item_combobox.get()
        unit_price = float(self.unit_price_entry.get())
        quantity = int(self.quantity_entry.get())
        date = self.date_entry.get_date()

        if not item_name or not unit_price or not quantity or not date:
            messagebox.showerror("Error", "All fields are required")
            return

        conn = sqlite3.connect('stationary_stock.db')
        cursor = conn.cursor()
        cursor.execute("SELECT id, total_stock, total_value FROM items WHERE name = ?", (item_name,))
        item = cursor.fetchone()
        if not item:
            messagebox.showerror("Error", "Item not found")
            return

        item_id, total_stock, total_value = item
        new_total_stock = total_stock + quantity
        new_total_value = total_value + (unit_price * quantity)

        cursor.execute("INSERT INTO stocks (item_id, date, unit_price, stock, initial_stock) VALUES (?, ?, ?, ?, ?)",
                       (item_id, date, unit_price, quantity, quantity))
        cursor.execute("UPDATE items SET total_stock = ?, total_value = ? WHERE id = ?",
                       (new_total_stock, new_total_value, item_id))

        conn.commit()
        conn.close()

        self.add_stock_window.destroy()
        self.load_items()

    def save_invoice(self):
        # Invoice generation logic goes here
        items = self.invoice_tree.get_children()
        if not items:
            messagebox.showerror("Error", "No items in the invoice")
            return

        pdf = FPDF()
        pdf.add_page()

        # Add sender address
        pdf.set_font("Arial", size=12)
        pdf.cell(200, 10, txt="Sender Address", ln=True, align="L")

        # Add invoice header
        pdf.set_font("Arial", size=16, style='B')
        pdf.cell(200, 10, txt="ADVICE OF DEBIT", ln=True, align="C")

        # Add receiver address
        pdf.set_font("Arial", size=12)
        pdf.cell(200, 10, txt="Receiver Address", ln=True, align="L")

        # Add branch details
        pdf.cell(200, 10, txt="Branch Number: XYZ, Account Number: 123456", ln=True, align="R")

        # Add date
        pdf.cell(200, 10, txt=f"STATIONERY CHARGES FOR {self.date_entry.get_date()}", ln=True, align="C")

        # Add table headers
        pdf.cell(40, 10, txt="Code", border=1)
        pdf.cell(40, 10, txt="Stationery", border=1)
        pdf.cell(40, 10, txt="Qty", border=1)
        pdf.cell(40, 10, txt="Price", border=1)
        pdf.cell(40, 10, txt="Cost", border=1)
        pdf.ln()

        # Add table rows
        total_cost = 0
        for item in items:
            values = self.invoice_tree.item(item, 'values')
            pdf.cell(40, 10, txt=str(values[0]), border=1)
            pdf.cell(40, 10, txt=str(values[1]), border=1)
            pdf.cell(40, 10, txt=str(values[2]), border=1)
            pdf.cell(40, 10, txt=str(values[3]), border=1)
            cost = float(values[2]) * float(values[3])
            total_cost += cost
            pdf.cell(40, 10, txt=str(cost), border=1)
            pdf.ln()

        # Add grand total
        pdf.cell(160, 10, txt="Grand Total", border=1)
        pdf.cell(40, 10, txt=str(total_cost), border=1)

        # Add authorized officer signature
        pdf.ln(20)
        pdf.cell(200, 10, txt="Authorized Officer Signature", ln=True, align="L")

        pdf.output("invoice.pdf")
        messagebox.showinfo("Success", "Invoice saved successfully")


if __name__ == '__main__':
    app = StationaryStockManager()
    app.mainloop()
