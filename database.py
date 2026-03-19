import sqlite3
import os

DB_PATH = 'ecommerce.db'

def init_db():
    # Connect to the SQLite database. If it doesn't exist, it will be created.
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Create the Orders table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Orders (
            OrderID TEXT PRIMARY KEY,
            CustomerName TEXT NOT NULL,
            DeliveryStatus TEXT NOT NULL
        )
    ''')

    # Insert some sample data for demonstration
    sample_orders = [
        ('1001', 'Chinedu Eze', 'Out for Delivery'),
        ('1002', 'Aisha Bello', 'Processing'),
        ('1003', 'Oluwaseun Ade', 'Delivered'),
        ('1004', 'Ngozi Okafor', 'Shipped')
    ]

    # Insert ignoring if they already exist
    cursor.executemany('''
        INSERT OR IGNORE INTO Orders (OrderID, CustomerName, DeliveryStatus)
        VALUES (?, ?, ?)
    ''', sample_orders)

    conn.commit()
    conn.close()
    print("Database initialized and sample data inserted successfully.")

if __name__ == '__main__':
    # Ensure we're in the right directory
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    init_db()
