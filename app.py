from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
from db import get_db_connection, initialize_database
from pdf_generator import create_expense_pdf

app = Flask(__name__)
CORS(app)

initialize_database()

@app.route('/register', methods=['POST'])
def register():
    data = request.json
    username = data['username']
    password = generate_password_hash(data['password'])

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, password))
    conn.commit()
    cursor.close()
    conn.close()

    return jsonify({'message': 'User registered successfully'}), 200

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data['username']
    password = data['password']

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
    user = cursor.fetchone()
    cursor.close()
    conn.close()

    if user and check_password_hash(user['password'], password):
        return jsonify({"message": "Login successful", "user_id": user['id']}), 200
    return jsonify({"message": "Invalid credentials"}), 401

@app.route('/add_expense', methods=['POST'])
def add_expense():
    data = request.json
    conn = get_db_connection()
    cursor = conn.cursor()
    query = "INSERT INTO expenses (user_id, title, amount, date) VALUES (%s, %s, %s, %s)"
    cursor.execute(query, (data['user_id'], data['title'], data['amount'], data['date']))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({'message': 'Expense added successfully'}), 200

@app.route('/get_yearly_expense/<int:user_id>/<int:year>', methods=['GET'])
def get_yearly_expense(user_id, year):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    query = "SELECT * FROM expenses WHERE user_id = %s AND YEAR(date) = %s"
    cursor.execute(query, (user_id, year))
    result = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(result)

@app.route('/generate_pdf/<int:user_id>/<int:month>/<int:year>', methods=['GET'])
def generate_pdf(user_id, month, year):
    pdf_path = create_expense_pdf(user_id, month, year)
    return send_file(pdf_path, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
