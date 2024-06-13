import sqlite3
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from status_and_stock_update import update_item_status


def fetch_data(db_path):
    update_item_status()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Fetch items data
    cursor.execute('SELECT code, name, total_stock, total_value FROM items WHERE total_value > 0')
    items_data = cursor.fetchall()

    # Calculate the sum of total_value
    cursor.execute('SELECT IFNULL(SUM(total_value), 0) FROM items')
    total_sum = cursor.fetchone()[0]

    conn.close()
    return items_data, total_sum


def generate_pdf(data, total_sum, pdf_path):
    doc = SimpleDocTemplate(pdf_path, pagesize=letter)
    styles = getSampleStyleSheet()
    elements = []

    # Title
    title = Paragraph("Items stock report", styles['Title'])
    elements.append(title)

    # Table data
    table_data = [['Code', 'Name', 'Qty', 'Total']]
    for row in data:
        table_data.append(row)

    # Create the table
    table = Table(table_data, colWidths=[0.75 * inch, 3.5 * inch, 0.75 * inch, 1 * inch])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.gray),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.whitesmoke),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))

    elements.append(table)

    # Add vertical space before total sum
    elements.append(Spacer(1, 0.5 * inch))  # Adjust the value to add more or less space

    # Create a style for right-aligned text
    right_align_style = ParagraphStyle(name='RightAlign', parent=styles['Normal'], alignment=2)

    # Add total sum with right-aligned text
    total_paragraph = Paragraph(f"Total Sum: {total_sum}", right_align_style)
    elements.append(total_paragraph)

    # Build the PDF
    doc.build(elements)
    print(f"PDF generated successfully: {pdf_path}")
