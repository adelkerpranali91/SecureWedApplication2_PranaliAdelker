#INSECURE APP.PY 
from flask import Flask, render_template, request, redirect, url_for, session, flash
from models.db_insecure import (
    init_db,
    create_user,
    get_user_by_email,
    # db helper
    get_conn,
    # appointment helpers
    create_appointment,
    get_appointment,
    get_appointment_id,
    update_appointment,
    delete_appointment,
)

#CORE FLASK APP INSTANCE
app = Flask(__name__)
app.secret_key = "dev-insecure-secret"  #WEAK FOR INSECURITY

#INITIALIZING DATABASE
with app.app_context():
    init_db()

#LANDING PAGE- REDIRECT BASED ON LOGIN STATUS
@app.route("/")
def index():
    if "email" in session:
        full_name = session.get("full_name", "")
        role = session.get("role", "")
        return render_template("index.html", full_name=full_name, role=role)
    return redirect(url_for("login"))

#DASHBOARD
@app.route("/dashboard")
def dashboard():
    if "email" not in session:
        flash("Please login first")
        return redirect(url_for("login"))
    #SHOW APPOINTMENT ON DASHBOARD
    apts = get_appointment()
    return render_template(
        "index.html",
        full_name=session.get("full_name", ""),
        role=session.get("role", ""),
        email=session.get("email", ""),
        appointments=apts
    )

#REGISTRATION
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        # FEILDS
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "").strip()
        confirm = request.form.get("confirm_password", "").strip()
        role = request.form.get("role", "patient")
        full_name = request.form.get("full_name", "").strip()
        phone = request.form.get("phone", "").strip()
        dob = request.form.get("date_of_birth", "").strip()
        address = request.form.get("address", "").strip()
        emergency_name = request.form.get("emergency_name", "").strip()
        emergency_phone = request.form.get("emergency_phone", "").strip()
        insurance = request.form.get("insurance_number", "").strip()

        required = [email, password, confirm, full_name, phone, dob, address, emergency_name, emergency_phone]
        if any(not v for v in required):
            flash("Please fill all required fields")
            return redirect(url_for("register"))
        if password != confirm:
            flash("Passwords do not match.")
            return redirect(url_for("register"))
        if get_user_by_email(email):
            flash("Email already registered.")
            return redirect(url_for("register"))

        #CREATE USER
        try:
            create_user(email, password, role, full_name, phone, dob, address, emergency_name, emergency_phone, insurance)
        except Exception as e:
            flash(f"Error creating user: {e}")
            return redirect(url_for("register"))

        flash("Registered (insecure). Please log in.")
        return redirect(url_for("login"))

    return render_template("auth/register.html")

#LOGIN
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "").strip()

        user = get_user_by_email(email)
        #PASSWORD SAVED AS PLAINTEXT
        if user and user.get("password") == password:
            # FEILD STORE IN SESSIONS
            session["email"] = user.get("email")
            session["full_name"] = user.get("full_name")
            session["role"] = user.get("role")
            flash("Logged in (insecure).")

            return redirect(url_for("dashboard"))

        flash("Invalid credentials")
        return redirect(url_for("login"))
    return render_template("auth/login.html")

@app.route("/logout")
def logout():
    session.clear()
    flash("Logged out")
    return redirect(url_for("login"))

#APPOINTMENT
@app.route("/appointments")
def appointments():
    if "email" not in session:
        flash("Please login first")
        return redirect(url_for("login"))
    #REDIRECT TO DASHBOARD IF LOGIN FAILED
    return redirect(url_for("dashboard"))

# CREATE APPOINTMENT
@app.route('/appointments/create', methods=['GET', 'POST'])
def create_appointment_():
    if request.method == 'POST':
        patient_name = request.form.get('patient_name', '').strip()
        doctor_name = request.form.get('doctor_name', '').strip()
        date = request.form.get('date', '').strip()
        time = request.form.get('time', '').strip()
        reason = request.form.get('reason', '').strip()

        #ALL FEILD ARE FILLED
        if not patient_name or not doctor_name or not date or not time:
            flash("Please fill all required fields.")
            return redirect(url_for('create_appointment_'))

        create_appointment(patient_name, doctor_name, date, time, reason)

        flash("Appointment created successfully.")
        return redirect(url_for('dashboard'))

    # LOAD THE DOCTORS FROM THE TABLE
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("SELECT full_name FROM users WHERE role='doctor' ORDER BY full_name;")
    rows = cur.fetchall()
    conn.close()
    doctors = [dict(r) for r in rows] if rows else []

    return render_template(
        "appointments/booking.html",
        patient_name=session.get("full_name", ""),
        doctors=doctors
    )

#EDIT APPOINTMENT
@app.route("/appointments/edit/<int:apt_id>", methods=["GET", "POST"])
def edit_appointment_(apt_id):
    if "email" not in session:
        flash("Please login first")
        return redirect(url_for("login"))

    apt = get_appointment_id(apt_id)
    if not apt:
        flash("Appointment not found")
        return redirect(url_for("dashboard"))

    #ANY USER COULD EDIT APPOINTMENT
    if request.method == "POST":
        patient_username = request.form.get("patient_username", apt["patient_username"])
        doctor_name = request.form.get("doctor_name", apt["doctor_name"])
        date = request.form.get("date", apt["date"])
        time = request.form.get("time", apt["time"])
        reason = request.form.get("reason", apt["reason"])

        update_appointment(apt_id, patient_username, doctor_name, date, time, reason)
        flash("Appointment updated (insecure).")
        return redirect(url_for("dashboard"))

    return render_template("appointments/edit.html", appointment=apt)

#APPOINTMNET DELETEION
@app.route("/appointments/delete/<int:apt_id>", methods=["GET", "POST"])
def delete_appointment_(apt_id):
    if "email" not in session:
        flash("Please login first")
        return redirect(url_for("login"))

    apt = get_appointment_id(apt_id)
    if not apt:
        flash("Appointment not found")
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        delete_appointment(apt_id)
        flash("Appointment deleted (insecure).")
        return redirect(url_for("dashboard"))

    return render_template("appointments/delete_confirm.html", appointment=apt)

if __name__ == "__main__":
    app.run(debug=True)
