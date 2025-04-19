from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from db import get_db_connection, initialize_database
from pdf_generator import create_expense_pdf  # ✅ Use your custom PDF module

app = Flask(__name__)
CORS(app)

# Initialize DB and create table
initialize_database()

@app.route('/add_expense', methods=['POST'])
def add_expense():
    data = request.json
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        query = "INSERT INTO expenses (title, amount, date) VALUES (%s, %s, %s)"
        cursor.execute(query, (data['title'], data['amount'], data['date']))
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({'message': 'Expense added successfully'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/get_yearly_expense/<int:year>', methods=['GET'])
def get_yearly_expense(year):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        query = "SELECT * FROM expenses WHERE YEAR(date) = %s"
        cursor.execute(query, (year,))
        result = cursor.fetchall()
        cursor.close()
        conn.close()
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/generate_pdf/<int:month>/<int:year>', methods=['GET'])
def generate_pdf(month, year):
    try:
        pdf_path = create_expense_pdf(month, year)
        return send_file(pdf_path, as_attachment=True)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
