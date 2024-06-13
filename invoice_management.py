import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from fpdf import FPDF
from datetime import datetime
from files_and_path_generator import generate_pdf_filename
from remove_empty_stocks import remove_empty_stocks
from status_and_stock_update import update_item_status


class InvoiceManagement:
    def __init__(self, parent):
        self.db_path = 'stationary_stock.db'
        self.items = None
        self.item_quantity_entry = None
        self.item_combobox = None
        self.add_item_button = None
        self.new_invoice_item_window = None
        self.save_invoice_button = None
        self.grand_total_label = None
        self.invoice_tree = None
        self.branch_combobox = None
        self.branch_frame = None
        self.invoice_frame = None
        self.parent = parent
        self.create_widgets()
        self.temp_stock = {}  # Dictionary to keep track of temporary stock levels
        self.invoice_items = []  # List to keep track of invoice items
        self.added_stock_counts = {}  # Dictionary to track added stock counts for each item

    def create_widgets(self):
        self.invoice_frame = ttk.Frame(self.parent)
        self.invoice_frame.pack(expand=1, fill="both")

        self.branch_frame = ttk.Frame(self.invoice_frame)
        self.branch_frame.pack(fill="x", padx=10, pady=10)

        tk.Label(self.branch_frame, text="Branch").pack(side=tk.LEFT)
        self.branch_combobox = ttk.Combobox(self.branch_frame)
        self.branch_combobox.pack(side=tk.LEFT, padx=10)
        self.populate_branch_combobox()

        self.invoice_tree = ttk.Treeview(self.invoice_frame, columns=(
            "item_code", "item_name", "quantity", "unit_price", "total_value", "remove"),
                                         show="headings")
        self.invoice_tree.heading("item_code", text="Item Code")
        self.invoice_tree.heading("item_name", text="Item Name")
        self.invoice_tree.heading("quantity", text="Quantity")
        self.invoice_tree.heading("unit_price", text="Unit Price")
        self.invoice_tree.heading("total_value", text="Total Value")
        self.invoice_tree.heading("remove", text="Remove")

        self.invoice_tree.pack(fill=tk.BOTH, expand=1)
        self.invoice_tree.bind("<Double-1>", self.handle_remove_item)  # Bind double-click event for removal

        self.add_item_button = tk.Button(self.invoice_frame, text="Add Item to Invoice", command=self.add_invoice_item)
        self.add_item_button.pack(side=tk.LEFT, padx=10, pady=10)

        self.save_invoice_button = tk.Button(self.invoice_frame, text="Save Invoice", command=self.save_invoice)
        self.save_invoice_button.pack(side=tk.LEFT, padx=10, pady=10)

        self.save_invoice_button = tk.Button(self.invoice_frame, text="Clear invoice", command=self.clear_invoice)
        self.save_invoice_button.pack(side=tk.RIGHT, padx=10, pady=10)

        self.grand_total_label = tk.Label(self.invoice_frame, text="Grand Total: 0.00")
        self.grand_total_label.pack(side=tk.RIGHT, padx=10, pady=10)

    def populate_branch_combobox(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, code FROM branches")
        rows = cursor.fetchall()
        branches = ["{} - {} - {}".format(row[0], row[1], row[2]) for row in rows]
        self.branch_combobox['values'] = branches
        conn.close()

    def add_invoice_item(self):
        self.new_invoice_item_window = tk.Toplevel(self.parent)
        self.new_invoice_item_window.title("Add Item to Invoice")

        tk.Label(self.new_invoice_item_window, text="Item").grid(row=0, column=0, padx=10, pady=10)
        self.item_combobox = ttk.Combobox(self.new_invoice_item_window)
        self.item_combobox.grid(row=0, column=1, padx=10, pady=10)
        self.item_combobox.bind('<KeyRelease>', self.filter_item_combobox)
        self.populate_item_combobox()

        tk.Label(self.new_invoice_item_window, text="Quantity").grid(row=1, column=0, padx=10, pady=10)
        self.item_quantity_entry = tk.Entry(self.new_invoice_item_window)
        self.item_quantity_entry.grid(row=1, column=1, padx=10, pady=10)

        tk.Button(self.new_invoice_item_window, text="Add", command=self.check_and_add_item).grid(row=2, column=0,
                                                                                                  columnspan=2, pady=10)

    def populate_item_combobox(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT id, code, name FROM items")
        rows = cursor.fetchall()
        self.items = ["{} - {} ({})".format(row[0], row[1], row[2]) for row in rows]
        self.item_combobox['values'] = self.items
        conn.close()

    def filter_item_combobox(self, event):
        value = event.widget.get().lower()
        filtered_items = [item for item in self.items if value in item.lower()]
        self.item_combobox['values'] = filtered_items

        # Ensure the combobox dropdown is shown
        if filtered_items:
            self.item_combobox.event_generate('<Down>')

        # Set focus back to the entry part of the combobox
        self.item_combobox.icursor(tk.END)
        self.item_combobox.focus_set()

    def check_and_add_item(self):
        item = self.item_combobox.get()
        quantity = self.item_quantity_entry.get()

        if not item or not quantity:
            messagebox.showwarning("Input Error", "Please fill all fields.")
            return

        item_id = item.split(" - ")[0]
        item_code = item.split(" - ")[1].split(" ")[0]
        item_name = item.split("(", 1)[1].strip(")")

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT SUM(stock) FROM stocks WHERE item_id = ?", (item_id,))
        total_stock = cursor.fetchone()[0]

        # Handle the case where total_stock is None
        if total_stock is None:
            total_stock = 0

        already_added_quantity = self.added_stock_counts.get(item_id, 0)

        available_stock = total_stock - already_added_quantity

        if available_stock < int(quantity):
            messagebox.showwarning("Stock Error", f"There is not enough stock. Only {available_stock} available.")
            conn.close()
            return

        self.add_item_to_invoice(item_id, item_code, item_name, int(quantity))
        conn.close()
        self.new_invoice_item_window.destroy()

    def add_item_to_invoice(self, item_id, item_code, item_name, quantity):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, unit_price, stock FROM stocks WHERE item_id = ? AND stock > 0 ORDER BY date",
            (item_id,))
        stocks = cursor.fetchall()
        remaining_quantity = quantity

        while remaining_quantity > 0:
            if not stocks:
                messagebox.showwarning("Stock Error", "Not enough stock available.")
                return

            stock = stocks.pop(0)
            stock_id, unit_price, stock_quantity = stock
            used_quantity = min(remaining_quantity, stock_quantity)

            total_value = used_quantity * unit_price
            item = self.invoice_tree.insert("", tk.END, values=(
                item_code, item_name, used_quantity, unit_price, total_value, "Remove"))

            self.temp_stock[stock_id] = self.temp_stock.get(stock_id, 0) + used_quantity
            self.invoice_items.append((item_code, item_name, used_quantity, unit_price, total_value, stock_id))

            self.added_stock_counts[item_id] = self.added_stock_counts.get(item_id, 0) + used_quantity

            remaining_quantity -= used_quantity

        self.update_grand_total()
        conn.close()

    def handle_remove_item(self, event):
        selected_item = self.invoice_tree.selection()[0]
        values = self.invoice_tree.item(selected_item, "values")
        item_code, item_name, quantity, unit_price, total_value, _ = values

        for entry in self.invoice_items:
            if entry[:5] == values:
                stock_id = entry[5]
                self.temp_stock[stock_id] -= int(quantity)
                self.invoice_items.remove(entry)
                break

        self.invoice_tree.delete(selected_item)
        self.added_stock_counts[item_code.split(" ")[0]] -= int(quantity)
        self.update_grand_total()

    def update_grand_total(self):
        grand_total = sum(float(self.invoice_tree.set(item, "total_value")) for item in self.invoice_tree.get_children())
        self.grand_total_label.config(text=f"Grand Total: {grand_total:.2f}")

    def save_invoice(self):
        branch = self.branch_combobox.get()

        if not branch:
            messagebox.showwarning("Input Error", "Please select a branch.")
            return

        branch_name = branch.split(" - ")[1]
        branch_code = branch.split(" - ")[2]

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        for stock_id, used_quantity in self.temp_stock.items():
            cursor.execute("UPDATE stocks SET stock = stock - ? WHERE id = ?", (used_quantity, stock_id))

        conn.commit()
        conn.close()

        self.generate_pdf(branch_name, branch_code)
        messagebox.showinfo("Invoice Saved", "The invoice has been saved successfully.")

        remove_empty_stocks(self.db_path)
        update_item_status()

        self.clear_invoice()

    def clear_invoice(self):
        self.temp_stock.clear()
        self.invoice_items.clear()
        self.added_stock_counts.clear()
        self.invoice_tree.delete(*self.invoice_tree.get_children())
        self.update_grand_total()

    def generate_pdf(self, branch_name, branch_code):
        pdf = FPDF()
        pdf.add_page()

        pdf.set_font("Arial", size=12)
        pdf.cell(200, 10, txt="Central Province Office, Kandy", ln=True, align="L")
        pdf.cell(200, 10, txt="ADVICE OF DEBIT", ln=True, align="C")
        pdf.cell(200, 8, txt=f"Branch Code: {branch_code}", ln=True, align="L")
        pdf.cell(200, 8, txt=f"Branch Name: {branch_name}", ln=True, align="L")
        pdf.cell(200, 8, txt="G/L Account No. 11310020", ln=True, align="C")
        pdf.cell(200, 8, txt="Stationery Charges for - {}".format(datetime.now().strftime("%Y-%m-%d")), ln=True,
                 align="C")

        pdf.ln(10)
        pdf.set_font("Arial", size=10)
        pdf.cell(40, 10, txt="Code", border=1)
        pdf.cell(80, 10, txt="Stationery", border=1)
        pdf.cell(20, 10, txt="Qty", border=1)
        pdf.cell(20, 10, txt="Price", border=1)
        pdf.cell(30, 10, txt="Cost", border=1)
        pdf.ln()

        grand_total = 0
        for item in self.invoice_items:
            item_code, item_name, quantity, unit_price, total_value, _ = item
            pdf.cell(40, 10, txt=item_code, border=1)
            pdf.cell(80, 10, txt=item_name, border=1)
            pdf.cell(20, 10, txt=str(quantity), border=1)
            pdf.cell(20, 10, txt=f"{unit_price:.2f}", border=1)
            pdf.cell(30, 10, txt=f"{total_value:.2f}", border=1)
            pdf.ln()
            grand_total += total_value

        pdf.cell(160, 10, txt="Grand Total", border=1)
        pdf.cell(30, 10, txt=f"{grand_total:.2f}", border=1)
        pdf.ln(30)
        pdf.cell(200, 4, txt="..............................", ln=True, align="L")
        pdf.cell(200, 10, txt="Authorized Officer", ln=True, align="L")

        pdf.output(generate_pdf_filename(branch_code))


if __name__ == "__main__":
    root = tk.Tk()
    app = InvoiceManagement(root)
    root.mainloop()
