from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
from functools import wraps

app = Flask(__name__)
app.secret_key = "CHANGE_THIS_TO_A_RANDOM_SECRET_KEY"
DB = "users.db"
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD_HASH = generate_password_hash("Loldumbkid")

def db():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = db()
    conn.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT UNIQUE NOT NULL, password_hash TEXT NOT NULL)")
    conn.commit(); conn.close()

def admin_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if not session.get("admin"):
            return redirect(url_for("admin_login"))
        return f(*args, **kwargs)
    return wrapper

@app.route("/")
def home():
    return render_template("index.html", username=session.get("username"))

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form["username"].strip()
        password = request.form["password"]
        if not username or not password:
            flash("Username and password are required."); return redirect(url_for("signup"))
        try:
            conn = db(); conn.execute("INSERT INTO users (username, password_hash) VALUES (?, ?)", (username, generate_password_hash(password))); conn.commit(); conn.close()
            flash("Account created! You can now log in."); return redirect(url_for("login"))
        except sqlite3.IntegrityError:
            flash("That username is already taken."); return redirect(url_for("signup"))
    return render_template("signup.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"].strip(); password = request.form["password"]
        conn = db(); user = conn.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone(); conn.close()
        if user and check_password_hash(user["password_hash"], password):
            session["username"] = username; return redirect(url_for("home"))
        flash("Invalid username or password.")
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear(); return redirect(url_for("home"))

@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        if request.form["username"] == ADMIN_USERNAME and check_password_hash(ADMIN_PASSWORD_HASH, request.form["password"]):
            session["admin"] = True; return redirect(url_for("admin"))
        flash("Invalid admin login.")
    return render_template("admin_login.html")

@app.route("/admin")
@admin_required
def admin():
    conn = db(); users = conn.execute("SELECT id, username FROM users ORDER BY id DESC").fetchall(); conn.close()
    return render_template("admin.html", users=users)

@app.route("/admin/logout")
def admin_logout():
    session.pop("admin", None); return redirect(url_for("admin_login"))

if __name__ == "__main__":
    init_db(); app.run(debug=True)
