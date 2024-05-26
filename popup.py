import tkinter as tk
from tkinter import simpledialog, messagebox


# Function to open the popup window
def open_popup():
    # Create a top-level window
    popup = tk.Toplevel(root)
    popup.title("Popup Window")
    popup.geometry("300x200")  # Set the size of the popup window

    # Add a label to the popup window
    label = tk.Label(popup, text="This is a popup window")
    label.pack(pady=20)

    # Add a button to close the popup window
    close_button = tk.Button(popup, text="Close", command=popup.destroy)
    close_button.pack(pady=10)


# Create the main window
root = tk.Tk()
root.title("Main Window")
root.geometry("400x300")  # Set the size of the main window

# Add a button to the main window to open the popup
open_popup_button = tk.Button(root, text="Open Popup", command=open_popup)
open_popup_button.pack(pady=20)

# Start the main loop
root.mainloop()
