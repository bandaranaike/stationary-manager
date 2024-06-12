import sqlite3
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.styles import getSampleStyleSheet


def fetch_data(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Fetch items data
    cursor.execute('SELECT code, name, total_stock, total_value FROM items')
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
    title = Paragraph("Items Report", styles['Title'])
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

    # Add total sum
    total_paragraph = Paragraph(f"Total Sum: {total_sum}", styles['Normal'])
    elements.append(total_paragraph)

    # Build the PDF
    doc.build(elements)
    print(f"PDF generated successfully: {pdf_path}")


if __name__ == '__main__':
    db_path = 'stationary_stock.db'  # Adjust the path to your database if necessary
    pdf_path = 'items_report.pdf'  # Path to save the PDF

    data, total_sum = fetch_data(db_path)
    generate_pdf(data, total_sum, pdf_path)
