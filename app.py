import os
import sqlite3
import subprocess
from flask import Flask, request, render_template, redirect, url_for, session, send_file, jsonify

app = Flask(__name__)
app.secret_key = "super_secret_lab_key"

DB_FILE = "vulnerable_lab.db"

def init_db():
    """Initializes SQLite database with sample data and tables."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("DROP TABLE IF EXISTS users")
    cursor.execute("DROP TABLE IF EXISTS products")
    cursor.execute("DROP TABLE IF EXISTS user_emails")
    
    cursor.execute("""
        CREATE TABLE users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            password TEXT,
            role TEXT,
            secret TEXT,
            email TEXT
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
        INSERT INTO users (username, password, role, secret, email) VALUES (?, ?, ?, ?, ?)
    """, [
        ('admin', 'AdminPass2026!', 'administrator', 'FLAG{sql_injection_master}', 'admin@seclab.local'),
        ('alice', 'alice123', 'user', 'Alice secret notes: FLAG{idor_bypass_pro}', 'alice@seclab.local'),
        ('bob', 'password123', 'user', 'Bob secret notes: FLAG{privacy_matters}', 'bob@seclab.local'),
    ])
    
    # Insert dummy product records
    cursor.executemany("""
        INSERT INTO products (name, description, price) VALUES (?, ?, ?)
    """, [
        ('Cyber Shield Hardware', 'Enterprise firewall hardware appliance', 499.99),
        ('Tactical Hacker Hoodie', 'Heavyweight stealth black cotton hoodie', 59.99),
        ('Web Pentesting Bible', 'Comprehensive guide to ethical hacking', 34.50),
        ('Encrypted USB Drive', '256-bit AES hardware encrypted storage', 79.99)
    ])
    
    conn.commit()
    conn.close()

    # Create dummy documentation file for LFI lab
    os.makedirs("docs", exist_ok=True)
    with open("docs/lab_guide.txt", "w") as f:
        f.write("Welcome to the Security Lab Guide!\nExplore modules to learn secure coding practices.")
    with open("docs/confidential_backup.txt", "w") as f:
        f.write("FLAG{lfi_directory_traversal_found}\nServer Root Backup Config: DB_KEY=super_secret_db_123")

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
                session['email'] = user[5]
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
        cursor.execute("SELECT name, description, price FROM products WHERE name LIKE ?", (f"%{query}%",))
        products = cursor.fetchall()
        conn.close()
        
    return render_template('search.html', query=query, products=products)

# ==========================================
# 3. VULNERABILITY: Command Injection (RCE)
# ==========================================
@app.route('/ping', methods=['GET', 'POST'])
def ping():
    output = None
    if request.method == 'POST':
        target = request.form.get('host', '127.0.0.1')
        
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
    cursor.execute("SELECT id, username, role, secret, email FROM users WHERE id = ?", (user_id,))
    user_data = cursor.fetchone()
    conn.close()
    
    return render_template('profile.html', user_data=user_data)

# ==========================================
# 5. VULNERABILITY: Local File Inclusion (LFI / Directory Traversal)
# ==========================================
@app.route('/view_doc')
def view_doc():
    filename = request.args.get('file', 'lab_guide.txt')
    filepath = os.path.join("docs", filename)
    content = ""
    error = None
    
    # INTENTIONAL VULNERABILITY: No path traversal sanitization (e.g. ../../)
    try:
        if os.path.exists(filepath):
            with open(filepath, 'r') as f:
                content = f.read()
        else:
            error = f"File '{filepath}' not found."
    except Exception as e:
        error = str(e)
        
    return render_template('view_doc.html', filename=filename, content=content, error=error)

# ==========================================
# 6. VULNERABILITY: Cross-Site Request Forgery (CSRF)
# ==========================================
@app.route('/settings', methods=['GET', 'POST'])
def settings():
    message = None
    if request.method == 'POST':
        new_email = request.form.get('email', '')
        user_id = session.get('user_id', 1)
        
        # INTENTIONAL VULNERABILITY: No CSRF token validation on sensitive action
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET email = ? WHERE id = ?", (new_email, user_id))
        conn.commit()
        conn.close()
        
        session['email'] = new_email
        message = f"Profile email successfully updated to: {new_email}"
        
    return render_template('settings.html', message=message)

# ==========================================
# 7. VULNERABILITY: Information Disclosure (Comments / Hidden Endpoints)
# ==========================================
@app.route('/api/v1/system_info')
def system_info():
    # INTENTIONAL VULNERABILITY: Unauthenticated API exposing sensitive configuration
    return jsonify({
        "status": "online",
        "version": "v2.4.1-debug",
        "db_engine": "SQLite3",
        "internal_api_key": "FLAG{info_disclosure_api_leak_9921}",
        "admin_backup_email": "admin_backup@seclab.local"
    })

if __name__ == '__main__':
    init_db()
    print("Starting Enhanced Vulnerable Web Lab server on http://127.0.0.1:5000")
    app.run(host='127.0.0.1', port=5000, debug=True)
