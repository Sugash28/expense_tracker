from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
import os
from db import get_db_connection

def create_expense_pdf(month, year):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    query = "SELECT * FROM expenses WHERE MONTH(date) = %s AND YEAR(date) = %s"
    cursor.execute(query, (month, year))
    expenses = cursor.fetchall()
    cursor.close()
    conn.close()

    # Create the PDF
    filename = f"monthly_expense_{month}_{year}.pdf"
    filepath = os.path.join("generated_pdfs", filename)
    os.makedirs("generated_pdfs", exist_ok=True)

    c = canvas.Canvas(filepath, pagesize=A4)
    width, height = A4
    c.setFont("Helvetica-Bold", 16)
    c.drawString(200, height - 50, f"Expense Report - {month}/{year}")
    c.setFont("Helvetica", 12)
    y = height - 100

    for exp in expenses:
        c.drawString(50, y, f"{exp['date']} - ₹{exp['amount']} - {exp['title']}")
        y -= 20
        if y < 50:
            c.showPage()
            y = height - 50

    c.save()
    return filepath
