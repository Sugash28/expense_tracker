from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
from excel_db import (initialize_database, add_user, get_user, 
                     add_expense, get_yearly_expenses)
from pdf_generator import create_expense_pdf

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
    username = data['username']
    password = generate_password_hash(data['password'])
    
    try:
        user_id = add_user(username, password)
        return jsonify({'message': 'User registered successfully', 'user_id': user_id}), 200
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

if __name__ == '__main__':
    app.run(debug=True)