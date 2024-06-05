import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from db_utils import create_connection
from invoice_pdf import generate_pdf


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
        self.invoice_tree = ttk.Treeview(self.root,
                                         columns=("index", "stationary", "quantity", "unit_price", "total_value"),
                                         show='headings')
        self.invoice_tree.heading("index", text="Index")
        self.invoice_tree.heading("stationary", text="Stationary")
        self.invoice_tree.heading("quantity", text="Qty")
        self.invoice_tree.heading("unit_price", text="Price")
        self.invoice_tree.heading("total_value", text="Cost")
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
                print("quantity_needed:", quantity_needed)
                if quantity_needed <= 0:
                    raise ValueError("Quantity must be positive")

                total_price = 0
                remaining_quantity = quantity_needed
                print("remaining_quantity:", remaining_quantity)

                for unit_price, stock_quantity in stocks:

                    if remaining_quantity <= 0:
                        break
                    if stock_quantity >= remaining_quantity:
                        total_price += remaining_quantity * unit_price
                        remaining_quantity = 0
                        print("remaining_quantity 2 :", remaining_quantity)
                    else:
                        total_price += stock_quantity * unit_price
                        remaining_quantity -= stock_quantity
                        print("stock_quantity 2 :", stock_quantity)

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
                        rows_to_add.append((f"{code}", f"{name}", remaining_quantity, f"{unit_price:.2f}",
                                            f"{remaining_quantity * unit_price:.2f}"))
                        stock[2] -= remaining_quantity
                        remaining_quantity = 0
                    else:
                        rows_to_add.append((f"{code}", f"{name}", stock_quantity, f"{unit_price:.2f}",
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
            self.generate_pdf("invoice.pdf", self.invoice_tree)
            messagebox.showinfo("Success", "Invoice saved and PDF generated successfully")
            self.temp_stock_levels.clear()
            self.invoice_tree.delete(*self.invoice_tree.get_children())
            self.update_total_invoice_value()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save invoice: {e}")

    def generate_pdf(self, file_name):
        c = canvas.Canvas(file_name, pagesize=letter)
        width, height = letter

        # Page 1: Invoice Items
        c.setFont("Helvetica-Bold", 12)
        c.drawCentredString(width / 2.0, height - inch, "Invoice Items")

        c.setFont("Helvetica-Bold", 10)
        table_headers = ["Item", "Unit Price", "Quantity", "Total Value"]
        x_offsets = [0.5 * inch, 2.5 * inch, 4.0 * inch, 5.5 * inch]
        y_offset = height - 1.5 * inch
        for i, header in enumerate(table_headers):
            c.drawString(x_offsets[i], y_offset, header)

        y_offset -= 0.3 * inch
        c.setFont("Helvetica", 10)
        for row_id in self.invoice_tree.get_children():
            row_data = self.invoice_tree.item(row_id)['values']
            for i, item in enumerate(row_data):
                c.drawString(x_offsets[i], y_offset, str(item))
            y_offset -= 0.3 * inch
            if y_offset < inch:
                c.showPage()
                c.setFont("Helvetica-Bold", 12)
                c.drawCentredString(width / 2.0, height - inch, "Invoice Items (Continued)")
                y_offset = height - 1.5 * inch

        c.showPage()

        # Page 2: Additional Data
        c.setFont("Helvetica-Bold", 12)
        c.drawCentredString(width / 2.0, height - inch, "Additional Data")

        # Simulated additional data; replace this with actual data
        additional_data = [
            ("Date", "Index", "Stationary", "Qty", "Price", "Cost"),
            ("20-Jan", "70022", "Savings Pass Book", "4", "3,660.48", "14,641.92"),
            ("22-Mar", "10104", "Attendance Register (10x25 Small)", "1", "246.99", "246.99"),
            ("", "10945", "Pawning Loans Contract Forms", "2", "12,093.39", "24,186.78"),
            # Add the rest of your data here...
        ]

        y_offset = height - 1.5 * inch
        for row in additional_data:
            for i, item in enumerate(row):
                c.drawString(x_offsets[i % len(x_offsets)], y_offset, item)
            y_offset -= 0.3 * inch
            if y_offset < inch:
                c.showPage()
                c.setFont("Helvetica-Bold", 12)
                c.drawCentredString(width / 2.0, height - inch, "Additional Data (Continued)")
                y_offset = height - 1.5 * inch

        c.save()

    def update_total_invoice_value(self):
        total_value = 0.00
        for row_id in self.invoice_tree.get_children():
            row_data = self.invoice_tree.item(row_id)['values']
            total_value += float(row_data[3])
        self.total_invoice_value_label.config(text=f"Total Invoice Value: {total_value:.2f}")

    def __del__(self):
        # Close the database connection when the object is deleted
        self.conn.close()


def create_invoice_tab(tab_frame):
    InvoiceApp(tab_frame)


if __name__ == "__main__":
    root = tk.Tk()
    root.title("Invoice Application")
    app = InvoiceApp(root)
    root.mainloop()
