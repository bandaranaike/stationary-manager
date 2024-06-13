import tkinter as tk
from tkinter import ttk
from stock_management import StockManagement
from invoice_management import InvoiceManagement
from initialize_db import create_tables


class StationaryStockManager:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("BOC COP Stationery Stock Manager")

        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(expand=1, fill="both")

        self.create_tabs()

    def create_tabs(self):
        # Stock Management Tab
        stock_management_frame = ttk.Frame(self.notebook)
        self.notebook.add(stock_management_frame, text='Stock Management')
        StockManagement(stock_management_frame)

        # Invoice Management Tab
        invoice_management_frame = ttk.Frame(self.notebook)
        self.notebook.add(invoice_management_frame, text='Invoice Management')
        InvoiceManagement(invoice_management_frame)

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    try:
        app = StationaryStockManager()
        app.run()
    except Exception as e:
        create_tables()
