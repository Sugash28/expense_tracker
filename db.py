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
    try:
        # Drop existing tables to ensure clean initialization
        cursor.execute("DROP TABLE IF EXISTS expenses")
        cursor.execute("DROP TABLE IF EXISTS users")
        
        # Create users table
        cursor.execute("""
            CREATE TABLE users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(255) UNIQUE,
                password TEXT
            ) ENGINE=InnoDB
        """)
        
        # Create expenses table
        cursor.execute("""
            CREATE TABLE expenses (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT,
                title VARCHAR(255),
                amount DECIMAL(10, 2),
                date DATE,
                FOREIGN KEY (user_id) REFERENCES users(id)
                ON DELETE CASCADE
            ) ENGINE=InnoDB
        """)
        
        conn.commit()
        print("Database tables created successfully")
        
    except mysql.connector.Error as err:
        print(f"Database initialization error: {err}")
        conn.rollback()
        raise
    finally:
        cursor.close()
        conn.close()

# Add this function to verify table existence
def verify_tables():
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()
        print("Existing tables:", [table[0] for table in tables])
        
        cursor.execute("DESCRIBE users")
        print("\nUsers table structure:")
        for row in cursor.fetchall():
            print(row)
    except mysql.connector.Error as err:
        print(f"Verification error: {err}")
    finally:
        cursor.close()
        conn.close()