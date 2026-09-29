# 🎯 Cybersecurity Educational Vulnerable Web Application (Lab Environment)

This is an expanded, intentionally vulnerable web application built with Python Flask for teaching web application security concepts, vulnerability identification, exploitation principles, and secure coding practices.

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

## 📚 Educational Lab Modules & Challenges

### Module 1: SQL Injection (SQLi)
* **Location:** `/login`
* **Vulnerability Description:** User input from the login form is formatted directly into an SQL query string without parameterization.
* **Challenge:** Log in as `admin` without knowing the actual password.
* **Sample Payload:** Username: `' OR '1'='1` | Password: `any`

---

### Module 2: Reflected Cross-Site Scripting (XSS)
* **Location:** `/search?q=...`
* **Vulnerability Description:** The search query parameter is rendered directly in HTML without escaping or sanitization.
* **Challenge:** Trigger an alert box in the victim's browser.
* **Sample Payload:** `<script>alert('Reflected XSS Success!')</script>`

---

### Module 3: Command Injection (Remote Code Execution / RCE)
* **Location:** `/ping`
* **Vulnerability Description:** User input for target host is passed directly into a system shell call (`subprocess.check_output(shell=True)`).
* **Challenge:** Execute arbitrary system commands (e.g. directory listing).
* **Sample Payload (Windows):** `127.0.0.1 & dir`
* **Sample Payload (Linux/macOS):** `127.0.0.1 ; whoami`

---

### Module 4: Insecure Direct Object Reference (IDOR)
* **Location:** `/profile?user_id=1`
* **Vulnerability Description:** The application relies solely on the user-supplied `user_id` query parameter to retrieve confidential user records without session authorization checks.
* **Challenge:** Retrieve secrets belonging to other users.
* **Sample Payload:** Navigate to `/profile?user_id=2` or `/profile?user_id=3`.

---

### Module 5: Local File Inclusion (LFI / Directory Traversal)
* **Location:** `/view_doc?file=...`
* **Vulnerability Description:** The document viewer concatenates requested file path parameters without relative path sanitization (`../`).
* **Challenge:** Read sensitive server configuration files outside the target documentation folder.
* **Sample Payload:** `/view_doc?file=confidential_backup.txt` or `/view_doc?file=../app.py`

---

### Module 6: Cross-Site Request Forgery (CSRF)
* **Location:** `/settings`
* **Vulnerability Description:** State-changing POST requests (email updates) do not validate anti-CSRF tokens.
* **Challenge:** Demonstrate how an attacker-crafted HTML form can change an authenticated user's email address silently.

---

### Bonus Module 7: Unauthenticated Information Disclosure
* **Location:** `/api/v1/system_info`
* **Vulnerability Description:** Unauthenticated API endpoint returning internal diagnostic details, software versions, and API flags in JSON response.
* **Challenge:** Discover hidden API endpoints and extract sensitive configuration details.
