# generate_pdf.py
from reportlab.pdfgen import canvas
import os
from db import get_db_connection

def create_expense_pdf(user_id, month, year):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT title, amount, date FROM expenses
        WHERE user_id = %s AND MONTH(date) = %s AND YEAR(date) = %s
    """, (user_id, month, year))
    expenses = cursor.fetchall()
    cursor.close()
    conn.close()

    filename = f"expense_report_{user_id}_{month}_{year}.pdf"
    c = canvas.Canvas(filename)
    c.drawString(100, 800, f"Expense Report for {month}/{year}")

    y = 760
    for title, amount, date in expenses:
        c.drawString(100, y, f"{date} - {title}: Rs.{amount}")
        y -= 20

    c.save()
    return filename
