# 🎯 Cybersecurity Educational Vulnerable Web Application (Lab Environment)

This is a intentionally vulnerable web application built with Python Flask for teaching web application security concepts, vulnerability identification, exploitation principles, and secure coding practices.

> ⚠️ **WARNING**: This application contains intentionally weak security controls. Run it **ONLY** locally on `localhost` (127.0.0.1) in isolated lab environments. Do not expose this application to public networks or production servers.

---

## 🚀 Quickstart Guide

### 1. Requirements
* Python 3.8+
* `flask` package

### 2. Installation & Setup
```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run the application
python app.py
```
Open your browser and navigate to: [http://127.0.0.1:5000](http://127.0.0.1:5000)

---

## 📚 Educational Modules & Challenges

### Module 1: SQL Injection (SQLi)
* **Location:** `/login`
* **Vulnerability Description:** User input from the login form is formatted directly into an SQL query string without parameterization.
* **Challenge:** Log in as `admin` without knowing the actual password.
* **Sample Payload:**
  * Username: `' OR '1'='1`
  * Password: `any`
* **Vulnerable Code:**
  ```python
  query = f"SELECT * FROM users WHERE username = '{username}' AND password = '{password}'"
  cursor.execute(query)
  ```
* **Remediation (Secure Fix):** Use parameterized queries.
  ```python
  cursor.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
  ```

---

### Module 2: Reflected Cross-Site Scripting (XSS)
* **Location:** `/search?q=...`
* **Vulnerability Description:** The search query parameter is rendered directly in HTML without escaping or sanitization.
* **Challenge:** Trigger an alert box in the victim's browser.
* **Sample Payload:**
  ```html
  <script>alert('XSS Exploit Successful!');</script>
  ```
* **Vulnerable Code:**
  ```jinja2
  <h3>Search Results for: {{ query | safe }}</h3>
  ```
* **Remediation (Secure Fix):** Remove `| safe` filter so Jinja automatically HTML-escapes input.
  ```jinja2
  <h3>Search Results for: {{ query }}</h3>
  ```

---

### Module 3: Command Injection (Remote Command Execution)
* **Location:** `/ping`
* **Vulnerability Description:** User input for target host is passed directly into a system shell call (`os.system` / `subprocess.check_output(shell=True)`).
* **Challenge:** List files in the server directory or view system environment variables.
* **Sample Payload (Windows):**
  ```text
  127.0.0.1 & dir
  ```
* **Sample Payload (Linux/macOS):**
  ```text
  127.0.0.1 ; ls -la
  ```
* **Vulnerable Code:**
  ```python
  cmd = f"ping -n 2 {target}"
  subprocess.check_output(cmd, shell=True)
  ```
* **Remediation (Secure Fix):** Validate input (e.g. check for valid IP address) and avoid using `shell=True`.
  ```python
  import ipaddress
  try:
      ipaddress.ip_address(target)
      subprocess.check_output(["ping", "-n", "2", target], shell=False)
  except ValueError:
      return "Invalid IP address provided."
  ```

---

### Module 4: Insecure Direct Object Reference (IDOR)
* **Location:** `/profile?user_id=1`
* **Vulnerability Description:** The application relies solely on the user-supplied `user_id` query parameter to retrieve confidential user records without checking session ownership.
* **Challenge:** Retrieve secrets belonging to other users.
* **Sample Payload:**
  * Navigate to `/profile?user_id=1`, `/profile?user_id=2`, etc.
* **Vulnerable Code:**
  ```python
  user_id = request.args.get('user_id')
  cursor.execute("SELECT id, username, role, secret FROM users WHERE id = ?", (user_id,))
  ```
* **Remediation (Secure Fix):** Enforce strict access control checking logged-in session credentials.
  ```python
  if int(user_id) != session.get('user_id') and session.get('role') != 'administrator':
      return "Access Denied", 403
  ```

---

## 💡 Instructor Classroom Recommendations
1. Have students attempt to solve each module's challenge first.
2. Direct students to `app.py` to trace why the code failed to prevent the attack.
3. Assign students the task of refactoring `app.py` to fix all four vulnerabilities using the recommended secure coding patterns.
