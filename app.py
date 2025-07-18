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
    try:
        data = request.json
        
        # Validate required fields
        if not data or 'username' not in data or 'password' not in data:
            return jsonify({'message': 'Missing username or password'}), 400
            
        username = data['username'].strip()
        password = data['password']
        
        # Enhanced validation
        if not username or not password:
            return jsonify({'message': 'Empty username or password not allowed'}), 400
        
        # Validate username and password
        if len(username) < 3:
            return jsonify({'message': 'Username must be at least 3 characters'}), 400
        if len(password) < 6:
            return jsonify({'message': 'Password must be at least 6 characters'}), 400
        
        # Check for valid characters in username
        if not username.isalnum():
            return jsonify({'message': 'Username must contain only letters and numbers'}), 400
        
        # Check if username already exists
        existing_user = get_user(username)
        if existing_user:
            return jsonify({'message': 'Username already exists'}), 400
        
        # Create user
        password_hash = generate_password_hash(password)
        user_id = int(add_user(username, password_hash))  # Convert int64 to int
        
        return jsonify({
            'status': 'success',
            'message': 'User registered successfully',
            'user_id': user_id
        }), 200
        
    except Exception as e:
        print(f"Registration error: {str(e)}")  # Server-side logging
        return jsonify({
            'status': 'error',
            'message': 'Registration failed. Please try again.'
        }), 400

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
    
@app.route('/get_monthly_expenses/<int:user_id>/<int:month>/<int:year>', methods=['GET'])
def get_monthly_expenses(user_id, month, year):
    try:
        # Get expenses for the specified month and year
        expenses = get_monthly_expenses(user_id, month, year)
        return jsonify({
            'status': 'success',
            'expenses': expenses
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 400

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
        # Get expenses for the month
        expenses = get_monthly_expenses(user_id, month, year)
        
        if not expenses:
            return jsonify({
                'status': 'error',
                'message': 'No expenses found for the selected period'
            }), 404

        # Format expenses for analysis
        total_amount = sum(float(exp.get('amount', 0)) for exp in expenses)
        expense_text = f"Monthly expenses for {month}/{year}:\n"
        expense_text += "\n".join([
            f"- {exp.get('title', 'Unknown')}: ${exp.get('amount', '0')}"
            for exp in expenses
        ])
        
        try:
            # Call Groq AI for analysis
            response = client.chat.completions.create(
                model="llama3-70b-8192",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a financial advisor. Analyze these expenses and provide insights."
                    },
                    {
                        "role": "user",
                        "content": f"Total spend: ${total_amount}\n{expense_text}"
                    }
                ]
            )
            
            # Extract analysis from AI response
            analysis = response.choices[0].message.content
            
            return jsonify({
                'status': 'success',
                'analysis': analysis,
                'expenses': expenses
            }), 200
            
        except Exception as e:
            print(f"AI Analysis error: {str(e)}")  # Server-side logging
            return jsonify({
                'status': 'error',
                'message': 'Failed to generate AI analysis',
                'error_details': str(e)
            }), 500
            
    except Exception as e:
        print(f"Server error: {str(e)}")  # Server-side logging
        return jsonify({
            'status': 'error',
            'message': 'Server error occurred',
            'error_details': str(e)
        }), 500

if __name__ == '__main__':
    app.run(debug=True)