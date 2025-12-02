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

# INITIALIZE DATABASE
with app.app_context():
    init_db()


def _fetch_appointments_by_sql(sql, params=()):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(sql, params)
    rows = cur.fetchall()
    cols = [c[0] for c in cur.description] if cur.description else []
    conn.close()
    results = []
    for r in rows:
        results.append({cols[i]: r[i] for i in range(len(cols))})
    return results

def get_appointments_for_doctor(doctor_full_name):
    try:
        return _fetch_appointments_by_sql(
            "SELECT * FROM appointments WHERE doctor_name = ? ORDER BY date, time",
            (doctor_full_name,)
        )
    except Exception:
        all_appts = _fetch_appointments_by_sql("SELECT * FROM appointments ORDER BY date, time")
        return [a for a in all_appts if any(
            str(v).lower() == doctor_full_name.lower() for k, v in a.items() if 'doctor' in k.lower()
        )]

def get_appointments_for_patient(patient_identifier):
    try:
        return _fetch_appointments_by_sql(
            "SELECT * FROM appointments WHERE patient_name = ? ORDER BY date, time",
            (patient_identifier,)
        )
    except Exception:
        try:
            return _fetch_appointments_by_sql(
                "SELECT * FROM appointments WHERE patient_username = ? ORDER BY date, time",
                (patient_identifier,)
            )
        except Exception:
            all_appts = _fetch_appointments_by_sql("SELECT * FROM appointments ORDER BY date, time")
            return [a for a in all_appts if any(
                str(v).lower() == patient_identifier.lower() for k, v in a.items() if 'patient' in k.lower()
            )]



##LANDING PAGE - REDIRECT BASED ON LOGIN STATUS
@app.route("/")
def index():
    if "email" in session:
        full_name = session.get("full_name", "")
        role = session.get("role", "")
        return render_template("index.html", full_name=full_name, role=role)
    return redirect(url_for("login"))


# DASHBOARD
@app.route("/dashboard")
def dashboard():
    if "email" not in session:
        flash("Please login first")
        return redirect(url_for("login"))
 
    role = session.get("role", "")
    full_name = session.get("full_name", "")
    email = session.get("email", "")

    if role == "doctor":
        apts = get_appointments_for_doctor(full_name)
        doctors = []
    elif role == "patient":
        apts = get_appointments_for_patient(full_name)
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("SELECT id, full_name FROM users WHERE LOWER(role)=? ORDER BY full_name;", ("doctor",))
        rows = cur.fetchall()
        conn.close()
        doctors = [{"id": r[0], "full_name": r[1]} for r in rows] if rows else []
    else:
        apts = get_appointment()
        doctors = []

    return render_template(
        "index.html",
        full_name=full_name,
        role=role,
        email=email,
        appointments=apts,
        doctors=doctors
    )

    return render_template(
        "index.html",
        full_name=session.get("full_name", ""),
        role=session.get("role", ""),
        email=session.get("email", ""),
        appointments=apts,
        doctors=doctors
    )

# REGISTERATION
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST": 
        #FEILDS
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "").strip()
        confirm = request.form.get("confirm_password", "").strip()
        role = request.form.get("role", "patient").strip().lower()
        full_name = request.form.get("full_name", "").strip()
        phone = request.form.get("phone", "").strip()
        dob = request.form.get("date_of_birth", "").strip()
        address = request.form.get("address", "").strip()
        emergency_name = request.form.get("emergency_name", "").strip()
        emergency_phone = request.form.get("emergency_phone", "").strip()
        insurance = request.form.get("insurance_number", "").strip()

        required = [email, password, confirm, full_name, phone, dob, address, emergency_name, emergency_phone]
        if any(not v for v in required):
            flash("Please fill all required fields (email, password, full name, phone, DOB, address, emergency contact).")
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
        # PASSWORD SAVED AS PLAINTEXT
        if user and user.get("password") == password:
            # FEILD STORED IN SESSION
            session["email"] = user.get("email")
            session["full_name"] = user.get("full_name")
            session["role"] = user.get("role")
            flash("Logged in (insecure).")

            return redirect(url_for("dashboard"))

        flash("Invalid credentials")
        return redirect(url_for("login"))

    return render_template("auth/login.html")


#APPOINTMENT
@app.route("/appointments")
def appointments():
    if "email" not in session:
        flash("Please login first")
        return redirect(url_for("login"))
    #REDIRECT TO DASHBOARD IF LOGIN FAILED
    return redirect(url_for("dashboard"))


#CREATE APPOINTMENT
@app.route('/appointments/create', methods=['GET', 'POST'])
def create_appointment_():

    #ALLOWING PATIENT TO CREATE APPOINTMENT 
    if "email" not in session:
        flash("Please login first")
        return redirect(url_for("login"))

    if session.get("role") != "patient":
        flash("Only patients may create appointments.")
        return redirect(url_for("dashboard"))

    if request.method == 'POST':
        patient_name_from_form = request.form.get('patient_name', '').strip()
        patient_username = session.get("full_name", "") or patient_name_from_form

        doctor_name = request.form.get('doctor_name', '').strip()
        date = request.form.get('date', '').strip()
        time = request.form.get('time', '').strip()
        reason = request.form.get('reason', '').strip()

        if not patient_username or not doctor_name or not date or not time:
            flash("Please fill all required fields.")
            return redirect(url_for('create_appointment_'))

        #INTO DATABASE
        create_appointment(patient_username, doctor_name, date, time, reason)

        flash("Appointment created successfully.")
        return redirect(url_for('dashboard'))

    #LOAD DOCTORS FROM TABLE
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("SELECT id, full_name FROM users WHERE LOWER(role)=? ORDER BY full_name;", ("doctor",))
    rows = cur.fetchall()
    conn.close()

    doctors = [{"id": r[0], "full_name": r[1]} for r in rows] if rows else []

    return render_template(
        "appointments/booking.html",
        patient_name=session.get("full_name", ""),
        doctors=doctors
    )

#MANAGE APPOINTMENT
@app.route("/appointments/manage/<int:apt_id>", methods=["GET", "POST"])
def manage_appointment_view(apt_id):
    if "email" not in session:
        flash("Please login first")
        return redirect(url_for("login"))

    apt = get_appointment_id(apt_id)
    if not apt:
        flash("Appointment not found")
        return redirect(url_for("dashboard"))

    role = session.get("role", "")
    me = session.get("full_name", "")

    #AUTHORIZATION
    if role == "patient":
        if apt.get("patient_username") != me:
            flash("You are not authorised to manage this appointment.")
            return redirect(url_for("dashboard"))
    elif role == "doctor":
        if apt.get("doctor_name") != me:
            flash("You are not authorised to manage this appointment.")
            return redirect(url_for("dashboard"))
    else:
        flash("You are not authorised to manage appointments.")
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        action = request.form.get("action", "update")

        #DOCTOR
        if role == "doctor":
            #DOCTOE CAN MARK DONE
            if action == "done":
                new_status = "done" if apt.get("status") != "done" else "scheduled"
                update_appointment(
                    apt_id,
                    apt.get("patient_username"),
                    apt.get("doctor_name"),
                    apt.get("date"),
                    apt.get("time"),
                    apt.get("reason"),
                    status=new_status
                )
                flash("Appointment status updated.")
                return redirect(url_for("dashboard"))

            flash("Doctors may only mark appointments as done.")
            return redirect(url_for("manage_appointment_view", apt_id=apt_id))

        # PATIENTS
        if role == "patient":
            if action == "delete":
                # PATIENT DELETE APPOINMENT
                delete_appointment(apt_id)
                flash("Appointment deleted.")
                return redirect(url_for("dashboard"))

            patient_username = request.form.get("patient_username", apt.get("patient_username", "")).strip()
            doctor_name = request.form.get("doctor_name", apt.get("doctor_name", "")).strip()
            date = request.form.get("date", apt.get("date", "")).strip()
            time = request.form.get("time", apt.get("time", "")).strip()
            reason = request.form.get("reason", apt.get("reason", "")).strip()
            status = request.form.get("status", apt.get("status", "scheduled")).strip()

            patient_username = me

            if not patient_username or not doctor_name or not date or not time:
                flash("Please fill required fields.")
                return redirect(url_for("manage_appointment_view", apt_id=apt_id))

            update_appointment(apt_id, patient_username, doctor_name, date, time, reason, status=status)
            flash("Appointment updated.")
            return redirect(url_for("dashboard"))

    if role == "doctor":
        return render_template("appointments/view_doctor.html", appointment=apt)

    return render_template("appointments/edit.html", appointment=apt)


#DEBUG: VIEW SESSION
@app.route("/whoami")
def whoami():
    if "email" in session:
        return {"email": session.get("email"), "full_name": session.get("full_name"), "role": session.get("role")}
    return {"logged_in": False}


# DEBUG: SHOW DOCTOR ROWS
@app.route("/debug_doctors")
def debug_doctors():
    try:
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("SELECT id, full_name, role FROM users ORDER BY full_name;")
        rows = cur.fetchall()
        conn.close()
        # rows are tuples (id, full_name, role) — convert properly to dicts
        docs = [{"id": r[0], "full_name": r[1], "role": r[2]} for r in rows]
        return {"doctors_all": docs}
    except Exception as e:
        return {"error": str(e)}


#DEBUG:SHOW PATIENT NAME IN APPOINTMENT LIST  
@app.route("/debug_appts")
def debug_appts():
    try:
        conn = get_conn()
        cur = conn.cursor()

        # Get table schema (columns)
        cur.execute("PRAGMA table_info(appointments);")
        cols_raw = cur.fetchall()  # rows like (cid, name, type, notnull, dflt_value, pk)
        # Convert to plain dicts
        cols = [
            {"cid": c[0], "name": c[1], "type": c[2], "notnull": c[3], "dflt_value": c[4], "pk": c[5]}
            for c in cols_raw
        ]

        # Get all appointment rows
        cur.execute("SELECT * FROM appointments;")
        rows_raw = cur.fetchall()
        # Column names in order
        col_names = [c["name"] for c in cols]

        # Convert rows to list of dicts {colname: value}
        rows = []
        for r in rows_raw:
            # r may be a tuple or sqlite3.Row; convert to tuple/list first
            rvals = list(r)
            rows.append({col_names[i]: rvals[i] for i in range(len(col_names))})

        conn.close()
        return {"columns": cols, "rows": rows}
    except Exception as e:
        # return error text so the UI shows it plainly
        return {"error": str(e)}




if __name__ == "__main__":
    app.run(debug=True)
