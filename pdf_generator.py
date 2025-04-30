from reportlab.pdfgen import canvas
from excel_db import get_monthly_expenses

def create_expense_pdf(user_id, month, year):
    expenses = get_monthly_expenses(user_id, month, year)
    
    filename = f"expense_report_{user_id}_{month}_{year}.pdf"
    c = canvas.Canvas(filename)
    c.drawString(100, 800, f"Expense Report for {month}/{year}")

    y = 760
    for expense in expenses:
        c.drawString(100, y, f"{expense['date']} - {expense['title']}: Rs.{expense['amount']}")
        y -= 20

    c.save()
    return filename