from fpdf import FPDF
import os
from db import get_db_connection

def create_expense_pdf(user_id, month, year):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT title, amount, date FROM expenses WHERE user_id = %s AND MONTH(date) = %s AND YEAR(date) = %s",
                   (user_id, month, year))
    expenses = cursor.fetchall()
    cursor.close()
    conn.close()

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt=f"Monthly Expense Report ({month}/{year})", ln=True, align='C')
    pdf.ln(10)

    for title, amount, date in expenses:
        pdf.cell(200, 10, txt=f"{date}: {title} - Rs. {amount}", ln=True)

    file_path = f"expense_report_{user_id}_{month}_{year}.pdf"
    pdf.output(file_path)
    return file_path
