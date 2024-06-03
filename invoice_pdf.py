from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.units import inch


def generate_pdf(file_name, invoice_tree):
    # Create a canvas
    c = canvas.Canvas(file_name, pagesize=letter)
    width, height = letter

    # Title
    c.setFont("Helvetica-Bold", 12)
    c.drawCentredString(width / 2.0, height - inch, "ADVICE OF DEBIT")

    # Header
    c.setFont("Helvetica", 10)
    c.drawString(0.5 * inch, height - 1.2 * inch, "Central Province Office")
    c.drawString(0.5 * inch, height - 1.4 * inch, "Bank of Ceylon, Kandy.")
    c.drawString(0.5 * inch, height - 1.8 * inch, "The Chief Manager/ Senior Manager/Manager,")
    c.drawString(0.5 * inch, height - 2.0 * inch, "Bank of Ceylon, Alawathugoda")
    c.drawString(0.5 * inch, height - 2.4 * inch, "Dear Sir / Madam,")

    # Subheader
    c.setFont("Helvetica-Bold", 10)
    c.drawString(0.5 * inch, height - 2.8 * inch, "STATIONERY CHARGERS FOR 1st QUARTER 2023.")

    # Table headers
    c.setFont("Helvetica-Bold", 9)
    table_headers = ["Date", "Index", "Stationary", "Qty", "Price", "Cost"]
    x_offsets = [0.5 * inch, 1.5 * inch, 2.5 * inch, 4.5 * inch, 5.0 * inch, 6.0 * inch]
    for i, header in enumerate(table_headers):
        c.drawString(x_offsets[i], height - 3.2 * inch, header)

    # Data rows

    y = height - 3.6 * inch

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

    for row_id in invoice_tree.get_children():
        row_data = invoice_tree.item(row_id)['values']
        for i, item in enumerate(row_data):
            c.drawString(x_offsets[i], y_offset, str(item))
        y_offset -= 0.3 * inch
        if y_offset < inch:
            c.showPage()
            c.setFont("Helvetica-Bold", 12)
            c.drawCentredString(width / 2.0, height - inch, "Invoice Items (Continued)")
            y_offset = height - 1.5 * inch


    # Grand total
    c.setFont("Helvetica-Bold", 10)
    c.drawString(5.0 * inch, y, "Grand Total")
    c.drawString(6.0 * inch, y, "130,563.48")

    # Authorized Officer
    c.setFont("Helvetica", 10)
    c.drawString(0.5 * inch, y - 0.5 * inch, "Authorized Officer")

    # Save the PDF
    c.save()
