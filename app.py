from flask import Flask, render_template, request, redirect, url_for
from database import get_db_connection

app = Flask(__name__)

@app.route("/")
def home():
    connection = get_db_connection()

    cursor = connection.cursor()

    cursor.execute("SELECT COUNT(*) FROM students")

    total_students = cursor.fetchone()[0]

    connection.close()

    return render_template(
        "dashboard.html",
        total_students=total_students
    )

@app.route("/add_student", methods=["GET", "POST"])
def add_student():

    if request.method == "POST":
        roll_number = request.form["roll_number"]
        name = request.form["name"]
        department = request.form["department"]
        year = request.form["year"]

        connection = get_db_connection()

        connection.execute(
            "INSERT INTO students (roll_number, name, department, year) VALUES (?, ?, ?, ?)",
            (roll_number, name, department, year)
        )

        connection.commit()
        connection.close()

        return redirect(url_for("home"))

    return render_template("add_student.html")

@app.route("/view_students")
def view_students():

    connection = get_db_connection()

    students = connection.execute(
        "SELECT * FROM students"
    ).fetchall()

    connection.close()

    return render_template(
        "view_students.html",
        students=students
    )

@app.route("/mark_attendance", methods=["GET", "POST"])
def mark_attendance():

    connection = get_db_connection()

    if request.method == "POST":
        student_id = request.form["student_id"]
        date = request.form["date"]
        status = request.form["status"]

        connection.execute(
            "INSERT INTO attendance (student_id, date, status) VALUES (?, ?, ?)",
            (student_id, date, status)
        )

        connection.commit()
        connection.close()

        return redirect(url_for("home"))

    students = connection.execute(
        "SELECT * FROM students"
    ).fetchall()

    connection.close()

    return render_template(
        "mark_attendance.html",
        students=students
    )

@app.route("/view_attendance")
def view_attendance():

    connection = get_db_connection()

    attendance_records = connection.execute("""
        SELECT
            students.roll_number,
            students.name,
            attendance.date,
            attendance.status
        FROM attendance
        JOIN students
        ON attendance.student_id = students.id
        ORDER BY attendance.date DESC
    """).fetchall()

    connection.close()

    return render_template(
        "view_attendance.html",
        attendance_records=attendance_records
    )

@app.route("/attendance_report")
def attendance_report():

    connection = get_db_connection()

    reports = connection.execute("""
        SELECT
            students.roll_number,
            students.name,
            COUNT(attendance.id) AS total_classes,
            SUM(
                CASE
                    WHEN attendance.status = 'Present' THEN 1
                    ELSE 0
                END
            ) AS present_days
        FROM students
        LEFT JOIN attendance
        ON students.id = attendance.student_id
        GROUP BY students.id
    """).fetchall()

    connection.close()

    report_data = []

    for record in reports:
        total_classes = record["total_classes"]
        present_days = record["present_days"] or 0

        if total_classes > 0:
            percentage = round(
                (present_days / total_classes) * 100, 2
            )
        else:
            percentage = 0

        report_data.append({
            "roll_number": record["roll_number"],
            "name": record["name"],
            "total_classes": total_classes,
            "present_days": present_days,
            "percentage": percentage
        })

    return render_template(
        "attendance_report.html",
        reports=report_data
    )






if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)