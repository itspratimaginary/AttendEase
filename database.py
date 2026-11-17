import sqlite3

# Connect to database
def connect_db():
    connection = sqlite3.connect("attendease.db")
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


# Create database tables
def create_tables():
    connection = connect_db()
    cursor = connection.cursor()

    # Subjects table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS subjects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            code TEXT UNIQUE NOT NULL
        )
    """)

    # Attendance table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS attendance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            subject_id INTEGER NOT NULL,
            class_date TEXT NOT NULL,
            status TEXT NOT NULL CHECK(status IN ('Present', 'Absent')),
            FOREIGN KEY(subject_id)
                REFERENCES subjects(id)
                ON DELETE CASCADE,
            UNIQUE(subject_id, class_date)
        )
    """)

    connection.commit()
    connection.close()


# Add subject
def add_subject(name, code):
    connection = connect_db()
    cursor = connection.cursor()

    try:
        cursor.execute(
            "INSERT INTO subjects (name, code) VALUES (?, ?)",
            (name, code)
        )
        connection.commit()
        return True

    except sqlite3.IntegrityError:
        return False

    finally:
        connection.close()


# Get all subjects
def get_subjects():
    connection = connect_db()
    cursor = connection.cursor()

    cursor.execute("SELECT id, name, code FROM subjects")
    subjects = cursor.fetchall()

    connection.close()
    return subjects


# Delete subject
def delete_subject(subject_id):
    connection = connect_db()
    cursor = connection.cursor()

    cursor.execute(
        "DELETE FROM subjects WHERE id = ?",
        (subject_id,)
    )

    connection.commit()
    connection.close()


# Mark attendance
def mark_attendance(subject_id, class_date, status):
    connection = connect_db()
    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO attendance (subject_id, class_date, status)
        VALUES (?, ?, ?)
        ON CONFLICT(subject_id, class_date)
        DO UPDATE SET status = excluded.status
    """, (subject_id, class_date, status))

    connection.commit()
    connection.close()


# Get attendance records
def get_attendance():
    connection = connect_db()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT attendance.id,
               subjects.name,
               subjects.code,
               attendance.class_date,
               attendance.status
        FROM attendance
        JOIN subjects
        ON attendance.subject_id = subjects.id
        ORDER BY attendance.class_date DESC
    """)

    records = cursor.fetchall()
    connection.close()

    return records


# Get attendance statistics
def get_attendance_stats(subject_id):
    connection = connect_db()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            COUNT(*),
            SUM(CASE WHEN status = 'Present' THEN 1 ELSE 0 END)
        FROM attendance
        WHERE subject_id = ?
    """, (subject_id,))

    result = cursor.fetchone()
    connection.close()

    total = result[0] or 0
    present = result[1] or 0

    return total, present