import pandas as pd
import os
from datetime import datetime

# Define Excel file paths
USERS_FILE = 'users.xlsx'
EXPENSES_FILE = 'expenses.xlsx'

def initialize_database():
    """Initialize Excel files if they don't exist"""
    if not os.path.exists(USERS_FILE):
        users_df = pd.DataFrame(columns=['id', 'username', 'password'])
        users_df.to_excel(USERS_FILE, index=False)
        print("Users database created")

    if not os.path.exists(EXPENSES_FILE):
        expenses_df = pd.DataFrame(columns=['id', 'user_id', 'title', 'amount', 'date'])
        expenses_df.to_excel(EXPENSES_FILE, index=False)
        print("Expenses database created")

def get_next_id(filename):
    """Get next available ID for a table"""
    df = pd.read_excel(filename)
    return 1 if df.empty else df['id'].max() + 1

def add_user(username, password):
    """Add a new user to the users Excel file"""
    df = pd.read_excel(USERS_FILE)
    user_id = get_next_id(USERS_FILE)
    new_user = pd.DataFrame({'id': [user_id], 'username': [username], 'password': [password]})
    df = pd.concat([df, new_user], ignore_index=True)
    df.to_excel(USERS_FILE, index=False)
    return user_id

def get_user(username):
    """Get user by username"""
    df = pd.read_excel(USERS_FILE)
    user = df[df['username'] == username]
    return user.to_dict('records')[0] if not user.empty else None

def add_expense(user_id, title, amount, date):
    """Add a new expense"""
    df = pd.read_excel(EXPENSES_FILE)
    expense_id = get_next_id(EXPENSES_FILE)
    new_expense = pd.DataFrame({
        'id': [expense_id],
        'user_id': [user_id],
        'title': [title],
        'amount': [amount],
        'date': [date]
    })
    df = pd.concat([df, new_expense], ignore_index=True)
    df.to_excel(EXPENSES_FILE, index=False)
    return expense_id

def get_yearly_expenses(user_id, year):
    """Get expenses for a specific user and year"""
    df = pd.read_excel(EXPENSES_FILE)
    df['date'] = pd.to_datetime(df['date'])
    yearly_expenses = df[
        (df['user_id'] == user_id) & 
        (df['date'].dt.year == year)
    ]
    return yearly_expenses.to_dict('records')

def get_monthly_expenses(user_id, month, year):
    """Get expenses for a specific user, month and year"""
    df = pd.read_excel(EXPENSES_FILE)
    df['date'] = pd.to_datetime(df['date'])
    monthly_expenses = df[
        (df['user_id'] == user_id) & 
        (df['date'].dt.month == month) &
        (df['date'].dt.year == year)
    ]
    return monthly_expenses.to_dict('records')