import mysql.connector
from dotenv import load_dotenv
import os

load_dotenv()

MYSQL_CONFIG = {
    'user': os.getenv('MYSQL_USER'),
    'password': os.getenv('MYSQL_PASSWORD'),
    'host': os.getenv('MYSQL_HOST'),
    'port': int(os.getenv('MYSQL_PORT')),
    'database': os.getenv('MYSQL_DB')
}

def get_db_connection():
    return mysql.connector.connect(**MYSQL_CONFIG)

def initialize_database():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS expenses (
            id INT AUTO_INCREMENT PRIMARY KEY,
            title VARCHAR(255),
            amount DECIMAL(10,2),
            date DATE
        )
    """)
    conn.commit()
    cursor.close()
    conn.close()
