from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
from excel_db import (get_monthly_expenses, initialize_database, add_user, get_user, 
                     add_expense, get_yearly_expenses)
from pdf_generator import create_expense_pdf
from groq import Groq

app = Flask(__name__)
CORS(app)

# Initialize Excel databases
try:
    initialize_database()
except Exception as e:
    print(f"Database initialization failed: {e}")

@app.route('/register', methods=['POST'])
def register():
    data = request.json
    
    # Validate required fields
    if not data or 'username' not in data or 'password' not in data:
        return jsonify({'message': 'Missing username or password'}), 400
        
    username = data['username'].strip()
    password = data['password']
    
    # Validate username and password
    if len(username) < 3:
        return jsonify({'message': 'Username must be at least 3 characters'}), 400
    if len(password) < 6:
        return jsonify({'message': 'Password must be at least 6 characters'}), 400
    
    # Check if username already exists
    existing_user = get_user(username)
    if existing_user:
        return jsonify({'message': 'Username already exists'}), 400
    
    try:
        password_hash = generate_password_hash(password)
        user_id = add_user(username, password_hash)
        return jsonify({
            'message': 'User registered successfully',
            'user_id': user_id
        }), 200
    except Exception as e:
        return jsonify({'message': f'Registration failed: {str(e)}'}), 400

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data['username']
    password = data['password']

    user = get_user(username)
    if user and check_password_hash(user['password'], password):
        return jsonify({"message": "Login successful", "user_id": user['id']}), 200
    return jsonify({"message": "Invalid credentials"}), 401

@app.route('/add_expense', methods=['POST'])
def add_expense_route():
    data = request.json
    try:
        expense_id = add_expense(
            data['user_id'],
            data['title'],
            data['amount'],
            data['date']
        )
        return jsonify({'message': 'Expense added successfully', 'expense_id': expense_id}), 200
    except Exception as e:
        return jsonify({'message': f'Failed to add expense: {str(e)}'}), 400

@app.route('/get_yearly_expense/<int:user_id>/<int:year>', methods=['GET'])
def get_yearly_expense(user_id, year):
    try:
        expenses = get_yearly_expenses(user_id, year)
        return jsonify(expenses)
    except Exception as e:
        return jsonify({'message': f'Failed to get expenses: {str(e)}'}), 400

@app.route('/generate_pdf/<int:user_id>/<int:month>/<int:year>', methods=['GET'])
def generate_pdf(user_id, month, year):
    try:
        pdf_path = create_expense_pdf(user_id, month, year)
        return send_file(pdf_path, as_attachment=True)
    except Exception as e:
        return jsonify({'message': f'Failed to generate PDF: {str(e)}'}), 400


# Add this after your existing imports
client = Groq(api_key='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')

@app.route('/analyze_expenses/<int:user_id>/<int:month>/<int:year>', methods=['GET'])
def analyze_expenses(user_id, month, year):
    try:
        # Get monthly expenses
        monthly_expenses = get_monthly_expenses(user_id, month, year)
        
        # Format expenses for AI analysis
        expense_text = "\n".join([
            f"Title: {exp['title']}, Amount: {exp['amount']}, Date: {exp['date']}"
            for exp in monthly_expenses
        ])
        
        # Get AI analysis
        response = client.chat.completions.create(
            model="llama3-70b-8192",
            messages=[
                {
                    "role": "system",
                    "content": "You are a financial advisor. Analyze these monthly expenses and provide insights and recommendations:"
                },
                {
                    "role": "user",
                    "content": f"Monthly expenses for {month}/{year}:\n{expense_text}"
                }
            ]
        )
        
        analysis = response.choices[0].message.content
        
        return jsonify({
            'analysis': analysis,
            'expenses': monthly_expenses
        }), 200
        
    except Exception as e:
        return jsonify({'message': f'Analysis failed: {str(e)}'}), 400

if __name__ == '__main__':
    app.run(debug=True)