import sqlite3
from typing import List, Dict

DB_PATH = "clinic.db"

def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_conn()
    cur = conn.cursor()
    # CREATE USER TABLE - PASSWORD AS PLAINTEXT
    cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT, email TEXT UNIQUE NOT NULL,password TEXT NOT NULL,
        role TEXT NOT NULL DEFAULT 'patient', full_name TEXT NOT NULL,phone TEXT NOT NULL,date_of_birth TEXT NOT NULL,
        address TEXT NOT NULL,emergency_name TEXT NOT NULL,emergency_phone TEXT NOT NULL,insurance_number TEXT);
    """)
    # CREATE APPOINTMENT TABLE 
    cur.execute("""
    CREATE TABLE IF NOT EXISTS appointments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,patient_username TEXT NOT NULL,doctor_name TEXT NOT NULL,
        date TEXT NOT NULL,time TEXT NOT NULL,reason TEXT,created_at TEXT DEFAULT (datetime('now')));
    """)
    conn.commit()
    conn.close()

#CREATING USER
def create_user(email: str, password: str, role: str = "patient",
                full_name: str = "", phone: str = "", date_of_birth: str = "",
                address: str = "", emergency_name: str = "", emergency_phone: str = "",
                insurance_number: str = ""):
    conn = get_conn()
    cur = conn.cursor()
    #USE- f STRING
    sql = (
        "INSERT INTO users (email, password, role, full_name, phone, date_of_birth, address, emergency_name, emergency_phone, insurance_number) "
        f"VALUES ('{email}', '{password}', '{role}', '{(full_name or '')}', '{(phone or '')}', '{(date_of_birth or '')}', '{(address or '')}', '{(emergency_name or '')}', '{(emergency_phone or '')}', '{(insurance_number or '')}')"
    )
    cur.execute(sql)
    conn.commit()
    conn.close()

def get_user_by_email(email: str):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(f"SELECT * FROM users WHERE email = '{email}'")
    row = cur.fetchone()
    conn.close()
    return dict(row) if row else None

def get_user_by_identity(identity: str):
    """Find user by email (we keep this for compatibility)."""
    return get_user_by_email(identity)

#CRATING APPOINTMENT
def create_appointment(patient_username: str, doctor_name: str, date: str, time: str, reason: str):
    conn = get_conn()
    cur = conn.cursor()
    sql = f"INSERT INTO appointments (patient_username, doctor_name, date, time, reason) VALUES ('{patient_username}', '{doctor_name}', '{date}', '{time}', '{reason}')"
    cur.execute(sql)
    conn.commit()
    conn.close()

def update_appointment(apt_id: int, patient_username: str, doctor_name: str, date: str, time: str, reason: str):
    conn = get_conn()
    cur = conn.cursor()
    sql = f"UPDATE appointments SET patient_username = '{patient_username}', doctor_name = '{doctor_name}', date = '{date}', time = '{time}', reason = '{reason}' WHERE id = {apt_id}"
    cur.execute(sql)
    conn.commit()
    conn.close()

#APPOINTMNET DELETION
def delete_appointment(apt_id: int):
    conn = get_conn()
    cur = conn.cursor()
    sql = f"DELETE FROM appointments WHERE id = {apt_id}"
    cur.execute(sql)
    conn.commit()
    conn.close()

def get_appointment() -> List[Dict]:
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT * FROM appointments ORDER BY date, time")
    rows = cur.fetchall()
    conn.close()
    return [dict(r) for r in rows]

#APPOINTMENT ID
def get_appointment_id(apt_id: int):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(f"SELECT * FROM appointments WHERE id = {apt_id}")
    row = cur.fetchone()
    conn.close()
    return dict(row) if row else None
