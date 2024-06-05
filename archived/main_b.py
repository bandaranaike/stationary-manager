import tkinter as tk
from tkinter import ttk
from db_utils import create_connection
from stock_management import create_stock_management_tab
from invoice import create_invoice_tab


def create_main_window():
    global conn, root, notebook
    conn = create_connection("stationary_stock.db")

    root = tk.Tk()
    root.title("Stationary Stock Management")

    notebook = ttk.Notebook(root)
    notebook.pack(expand=True, fill='both')

    # Create tabs
    stock_frame = tk.Frame(notebook)
    notebook.add(stock_frame, text="Stock Management")
    create_stock_management_tab(stock_frame)

    invoice_frame = tk.Frame(notebook)
    notebook.add(invoice_frame, text="Invoice")
    create_invoice_tab(invoice_frame)

    root.mainloop()


if __name__ == "__main__":
    create_main_window()
