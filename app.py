from datetime import timedelta
import sqlite3
import subprocess
from flask import Flask, Response, render_template, request, redirect, url_for, flash, session
import os
from routes.home import home_router
from routes.note import note_router

app = Flask(__name__)
app.secret_key = os.urandom(24)

app.template_folder = "views"

@app.before_request
def setup_session():
    session["username"] = session.get("username", None)
    session["logged_in"] = session.get("logged_in", False)
    session.permanent = True
    # app.permanent_session_lifetime = timedelta(minutes=5)
    app.config["SESSION_COOKIE_HTTPONLY"] = False
    app.config["SESSION_COOKIE_SECURE"] = False
    app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
    if 'notes' not in session:
        session['notes'] = []

@app.after_request
def add_header(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    return response

app.register_blueprint(home_router)
app.register_blueprint(note_router)

def init_db():
    try:
        db = sqlite3.connect("data.db")
        cmd = """
        CREATE TABLE users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            is_admin INTEGER DEFAULT 0
        );
        INSERT INTO users (username, password, is_admin) VALUES ("admin", "admin", 1);
        INSERT INTO users (username, password, is_admin) VALUES ("test", "test", 0);
        """
        db.executescript(cmd)
        db.commit()
        db.close()
    except:
        print("Database already exists")
        pass

def create_user(username, password, is_admin):
    db = sqlite3.connect("data.db")
    db.execute("INSERT INTO users (username, password, is_admin) VALUES (?, ?, ?)", (username, password, is_admin))
    db.commit()
    db.close()

def get_users():
    db = sqlite3.connect("data.db")
    users = db.execute("SELECT * FROM users").fetchall()
    db.close()
    return users

def get_user(username):
    db = sqlite3.connect("data.db")
    user = db.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
    db.close()
    return user

def is_admin():
    return session.get("logged_in") and get_user(session.get("username"))[3] == 1

def escape(content):
    content = content.replace("&", "&amp;")
    content = content.replace("<", "&lt;")
    content = content.replace(">", "&gt;")
    return content

def run_command(command):
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True)
    return process.communicate()[0]

@app.route("/admin", methods=["GET", "POST"])
def admin_panel():
    # Check if the user is logged in and is an admin
    if not is_admin():
        # Clear the session and redirect to login
        session.clear()
        return redirect(url_for("login"))
    
    if request.method == "POST":
        cmd = request.form["cmd"]
        cmd_result = run_command(cmd)
        return Response(escape(cmd_result), content_type='text/plain')

    return render_template("admin.html")
        
        
@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        if get_user(username):
            flash("User already exists")
        else:
            create_user(username, password, 0)
            flash("User created successfully")
    return render_template("signup.html")

@app.route("/", methods=["GET", "POST"])
def login():
    if session.get("logged_in"):
        return redirect(url_for("home.home"))
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        user = get_user(username)
        if user and user[2] == password:
            session["username"] = username
            session["logged_in"] = True
            return redirect(url_for("home.home"))
        else:
            flash("Invalid username or password")
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

# @app.route("/")
# def index():
#     return "Hello World!"

init_db()

if __name__ == "__main__":    
    app.run(debug=False, host="0.0.0.0", port=5000)