import sqlite3

conn = sqlite3.connect('database.db')
c = conn.cursor()

# Create users table
c.execute('''
    CREATE TABLE users (
        id INTEGER PRIMARY KEY,
        username TEXT NOT NULL,
        password TEXT NOT NULL
    )
''')

# Insert a test user
c.execute('''
    INSERT INTO users (username, password)
    VALUES ('admin', 'password123')
''')

conn.commit()
conn.close()
