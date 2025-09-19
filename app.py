from flask import Flask, render_template, request, redirect, url_for, session, flash
import mysql.connector
import os

app = Flask(__name__)
app.secret_key = "super_secret_key"

# ✅ Database connection function
def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",       # change to your MySQL username
        password="12345", # change to your MySQL password
        database="farmiq"   # make sure you created this DB
    )

# ✅ Home route (redirects to login if not logged in)
@app.route('/')
def home():
    if "user_id" in session:
        return redirect(url_for("dashboard"))
    return redirect(url_for("login"))

# ✅ Login route
@app.route('/login', methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
        SELECT * FROM accounts 
        WHERE (email=%s OR mobile=%s) AND password=%s
        """, (email, email, password))
        user = cursor.fetchone()
        conn.close()

        if user:
            session["user_id"] = user["id"]
            session["email"] = user["email"]
            flash("Login successful!", "success")
            return redirect(url_for("dashboard"))
        else:
            flash("Invalid credentials, please try again.", "danger")
            return redirect(url_for("login"))

    return render_template("login.html")

# ✅ Signup route
# @app.route('/signup', methods=["GET", "POST"])
# def signup():
#     if request.method == "POST":
#         name = request.form["name"]
#         email = request.form["email"]
#         password = request.form["password"]

#         conn = get_db_connection()
#         cursor = conn.cursor()
#         cursor.execute("INSERT INTO users (name, email, password) VALUES (%s, %s, %s)", 
#                        (name, email, password))
#         conn.commit()
#         conn.close()

#         flash("Account created successfully! Please login.", "success")
#         return redirect(url_for("login"))

#     return render_template("signup.html")

# ✅ Dashboard route (only after login)

@app.route('/signup', methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        fullname = request.form.get("fullname")
        mobile = request.form.get("mobile")
        email = request.form.get("email")
        password = request.form.get("password")

        print("Form Data:", fullname, mobile, email, password)  # 👈 debug

        if not fullname or not mobile or not email or not password:
            flash("All fields are required!", "danger")
            return redirect(url_for("signup"))

        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO accounts (name, mobile, email, password) VALUES (%s, %s, %s, %s)",
                (fullname, mobile, email, password)
            )
            conn.commit()
            cursor.close()
            conn.close()
            print("✅ Data inserted successfully!")   # 👈 debug
        except Exception as e:
            print("❌ Database Error:", e)            # 👈 debug

        flash("Account created successfully! Please login.", "success")
        return redirect(url_for("login"))

    return render_template("signup.html")



@app.route('/dashboard')
def dashboard():
    if "user_id" not in session:
        flash("Please login first.", "warning")
        return redirect(url_for("login"))
    return render_template("dashboard.html", email=session["email"])

# ✅ Logout route
@app.route('/logout')
def logout():
    session.clear()
    flash("Logged out successfully!", "info")
    return redirect(url_for("login"))

# ✅ Custom 404 error page
@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404


if __name__ == "__main__":
    app.run(debug=True)
