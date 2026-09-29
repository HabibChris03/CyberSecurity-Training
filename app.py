import os
import sqlite3
import subprocess
from flask import Flask, request, render_template_string, render_template, redirect, url_for, session

app = Flask(__name__)
app.secret_key = "super_secret_lab_key"

DB_FILE = "vulnerable_lab.db"

def init_db():
    """Initializes an in-memory or file-based SQLite database with sample data."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("DROP TABLE IF EXISTS users")
    cursor.execute("DROP TABLE IF EXISTS products")
    
    cursor.execute("""
        CREATE TABLE users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            password TEXT,
            role TEXT,
            secret TEXT
        )
    """)
    
    cursor.execute("""
        CREATE TABLE products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            description TEXT,
            price REAL
        )
    """)
    
    # Insert dummy user records
    cursor.executemany("""
        INSERT INTO users (username, password, role, secret) VALUES (?, ?, ?, ?)
    """, [
        ('admin', 'AdminPass2026!', 'administrator', 'FLAG{sql_injection_master}'),
        ('alice', 'alice123', 'user', 'Alice loves cats'),
        ('bob', 'password123', 'user', 'Bob secret notes'),
    ])
    
    # Insert dummy product records
    cursor.executemany("""
        INSERT INTO products (name, description, price) VALUES (?, ?, ?)
    """, [
        ('Cyber Shield', 'Ultimate protection hardware', 299.99),
        ('Hacker Hoodie', 'Comfortable black cotton hoodie', 49.99),
        ('Security Book', 'Introduction to Ethical Hacking', 25.00),
    ])
    
    conn.commit()
    conn.close()

@app.route('/')
def home():
    user = session.get('username', 'Guest')
    return render_template('index.html', user=user)

# ==========================================
# 1. VULNERABILITY: SQL Injection (SQLi)
# ==========================================
@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form.get('username', '')
        password = request.form.get('password', '')
        
        # INTENTIONAL VULNERABILITY: Unsafe string formatting allows SQLi
        # Example payload: ' OR '1'='1
        query = f"SELECT * FROM users WHERE username = '{username}' AND password = '{password}'"
        
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        try:
            cursor.execute(query)
            user = cursor.fetchone()
            conn.close()
            
            if user:
                session['username'] = user[1]
                session['role'] = user[3]
                session['user_id'] = user[0]
                return redirect(url_for('home'))
            else:
                error = "Invalid credentials!"
        except sqlite3.OperationalError as e:
            conn.close()
            error = f"Database Error: {e} (Executed Query: {query})"
            
    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))

# ==========================================
# 2. VULNERABILITY: Reflected XSS
# ==========================================
@app.route('/search')
def search():
    query = request.args.get('q', '')
    products = []
    if query:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        # Parameterized here to prevent SQLi in search, focusing only on XSS
        cursor.execute("SELECT name, description, price FROM products WHERE name LIKE ?", (f"%{query}%",))
        products = cursor.fetchall()
        conn.close()
        
    # INTENTIONAL VULNERABILITY: Query parameter rendered without HTML escaping
    # Example payload: <script>alert('XSS Exploit!')</script>
    return render_template('search.html', query=query, products=products)

# ==========================================
# 3. VULNERABILITY: Command Injection
# ==========================================
@app.route('/ping', methods=['GET', 'POST'])
def ping():
    output = None
    if request.method == 'POST':
        target = request.form.get('host', '127.0.0.1')
        
        # INTENTIONAL VULNERABILITY: Passing unsanitized user input into system shell
        # Windows payload example: 127.0.0.1 & dir
        # Linux payload example: 127.0.0.1 ; id
        cmd = f"ping -n 2 {target}" if os.name == 'nt' else f"ping -c 2 {target}"
        
        try:
            output = subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT, text=True)
        except subprocess.CalledProcessError as e:
            output = e.output
            
    return render_template('ping.html', output=output)

# ==========================================
# 4. VULNERABILITY: Insecure Direct Object Reference (IDOR)
# ==========================================
@app.route('/profile')
def profile():
    user_id = request.args.get('user_id')
    if not user_id:
        user_id = session.get('user_id', 1)
        
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    # INTENTIONAL VULNERABILITY: No authorization check to ensure session['user_id'] == user_id
    cursor.execute("SELECT id, username, role, secret FROM users WHERE id = ?", (user_id,))
    user_data = cursor.fetchone()
    conn.close()
    
    return render_template('profile.html', user_data=user_data)

if __name__ == '__main__':
    init_db()
    print("Starting Vulnerable Web Lab server on http://127.0.0.1:5000")
    print("WARNING: This server is intentionally insecure. Run only in local, isolated environments.")
    app.run(host='127.0.0.1', port=5000, debug=True)
