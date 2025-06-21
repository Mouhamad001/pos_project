import sqlite3
import os
from auth import get_password_hash

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./pos_system.db")
DB_FILE = DATABASE_URL.split("///")[-1]

def init_db_raw():
    db = sqlite3.connect(DB_FILE)
    cursor = db.cursor()

    # Create all tables using the provided schema
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY,
        email VARCHAR NOT NULL,
        username VARCHAR NOT NULL,
        hashed_password VARCHAR NOT NULL,
        is_active BOOLEAN,
        is_admin BOOLEAN,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY,
        name VARCHAR NOT NULL,
        description VARCHAR,
        price FLOAT NOT NULL,
        stock INTEGER,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS customers (
        id INTEGER PRIMARY KEY,
        name VARCHAR NOT NULL,
        email VARCHAR,
        phone VARCHAR,
        address VARCHAR,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(email)
    );
    """)
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS sales (
        id INTEGER PRIMARY KEY,
        customer_id INTEGER,
        user_id INTEGER NOT NULL,
        total_amount FLOAT NOT NULL,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(customer_id) REFERENCES customers(id),
        FOREIGN KEY(user_id) REFERENCES users(id)
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS sale_items (
        id INTEGER PRIMARY KEY,
        sale_id INTEGER NOT NULL,
        product_id INTEGER NOT NULL,
        quantity INTEGER NOT NULL,
        price FLOAT NOT NULL,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(sale_id) REFERENCES sales(id),
        FOREIGN KEY(product_id) REFERENCES products(id)
    );
    """)

    print("Tables created or already exist.")

    # Create admin user
    try:
        hashed_password = get_password_hash("admin123")
        cursor.execute(
            "INSERT INTO users (username, email, hashed_password, is_active, is_admin) VALUES (?, ?, ?, ?, ?)",
            ("admin", "admin@example.com", hashed_password, True, True)
        )
        print("Admin user created.")
    except sqlite3.IntegrityError:
        print("Admin user already exists.")

    db.commit()
    db.close()

if __name__ == "__main__":
    print("Initializing database with raw SQL...")
    init_db_raw()
    print("Database initialization complete.") 