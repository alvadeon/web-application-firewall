from flask import Flask, request, redirect, url_for, render_template, flash
import sqlite3
import logging
from waf import check_sql_injection, check_xss_and_command_injection  # Import the necessary functions from your WAF module

app = Flask(__name__)
app.secret_key = 'your_secret_key'

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # Call WAF check_sql_injection function
        ip = request.remote_addr
        result = check_sql_injection(ip, f"{username} {password}")
        if "Blocked" in result:
            return result

        # Sanitize input to prevent SQL injection
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
        user = c.fetchone()
        conn.close()
        
        if user:
            return redirect(url_for('index'))
        else:
            flash('Invalid credentials')
            return redirect(url_for('login'))
    return render_template('login.html')

@app.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == 'POST':
        query = request.form['query']
        ip = request.remote_addr
        
        # Call WAF check_xss_and_command_injection function
        result = check_xss_and_command_injection(ip, query)
        if "Blocked" in result:
            return result
        
        # Display the search query to simulate a search result
        return f"Search results for: {query}"
    return render_template('search.html')

if __name__ == "__main__":
    app.run(port=5000)
