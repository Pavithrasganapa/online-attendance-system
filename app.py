from flask import Flask, render_template, request, redirect
import sqlite3
from datetime import date
import os

app = Flask(__name__)

# Create DB
def init_db():

    DB_PATH = os.path.join(os.getcwd(), "attendance.db")
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    cur = conn.cursor()

    cur.execute('''
    CREATE TABLE IF NOT EXISTS students(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT
    )
    ''')

    cur.execute('''
    CREATE TABLE IF NOT EXISTS attendance(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id INTEGER,
        status TEXT,
        date TEXT
    )
    ''')

    cur.execute('''
CREATE TABLE IF NOT EXISTS students(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    usn TEXT UNIQUE,
    name TEXT
)
''')

    conn.commit()
    conn.close()

init_db()

# Home - Add Student
@app.route("/", methods=["GET","POST"])
def index():
    conn = sqlite3.connect('attendance.db')
    cur = conn.cursor()

    if request.method == "POST":
        name = request.form['name']
        cur.execute("INSERT INTO students(name) VALUES(?)", (name,))
        conn.commit()

    cur.execute("SELECT * FROM students")
    students = cur.fetchall()

    conn.close()
    return render_template("index.html", students=students)

# Mark Attendance
@app.route("/mark", methods=["GET","POST"])
def mark():
    conn = sqlite3.connect('attendance.db')
    cur = conn.cursor()

    cur.execute("SELECT * FROM students")
    students = cur.fetchall()

    if request.method == "POST":
        for student in students:
            status = request.form.get(str(student[0]))
            cur.execute(
                "INSERT INTO attendance(student_id,status,date) VALUES(?,?,?)",
                (student[0], status, str(date.today()))
            )
        conn.commit()
        return redirect("/report")

    conn.close()
    return render_template("mark.html", students=students)

# Report
@app.route("/report")
def report():
    conn = sqlite3.connect('attendance.db')
    cur = conn.cursor()

    cur.execute('''
    SELECT students.name, attendance.status, attendance.date
    FROM attendance
    JOIN students ON students.id = attendance.student_id
    ''')

    records = cur.fetchall()
    conn.close()

    return render_template("report.html", records=records)

message = ""

if request.method == "POST":
    full_input = request.form.get('name')

    if "-" not in full_input:
        message = "Enter in format: USN - Name"
    else:
        usn, name = full_input.split("-", 1)
        usn = usn.strip()
        name = name.strip()

        # Check duplicate USN
        cur.execute("SELECT * FROM students WHERE usn = ?", (usn,))
        if cur.fetchone():
            message = "⚠️ USN already exists! Student already entered."
        else:
            cur.execute(
                "INSERT INTO students(usn, name) VALUES(?, ?)",
                (usn, name)
            )
            conn.commit()

if __name__ == "__main__":
    # app.run(debug=True)
    app.run(host="0.0.0.0", port=5000)