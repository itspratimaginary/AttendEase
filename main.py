import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import date
import csv
import math

from database import (
    create_tables,
    add_subject as add_subject_to_db,
    get_subjects,
    delete_subject as delete_subject_from_db,
    mark_attendance,
    get_attendance,
    get_attendance_stats
)

# Initialize database
create_tables()

# ---------------- MAIN WINDOW ----------------

root = tk.Tk()
root.title("AttendEase - Student Attendance Management")
root.geometry("1100x700")
root.configure(bg="#F4F6FA")
root.minsize(900, 600)

# ---------------- COLOURS ----------------

BG = "#F4F6FA"
SIDEBAR = "#1E293B"
WHITE = "#FFFFFF"
BLUE = "#2563EB"
TEXT = "#1E293B"
GREY = "#64748B"
GREEN = "#16A34A"
RED = "#DC2626"

TARGET = 75

# ---------------- SIDEBAR ----------------

sidebar = tk.Frame(root, bg=SIDEBAR, width=230)
sidebar.pack(side="left", fill="y")
sidebar.pack_propagate(False)

tk.Label(
    sidebar,
    text="AttendEase",
    font=("Arial", 23, "bold"),
    bg=SIDEBAR,
    fg="white"
).pack(pady=(35, 5))

tk.Label(
    sidebar,
    text="STUDENT ATTENDANCE SYSTEM",
    font=("Arial", 8),
    bg=SIDEBAR,
    fg="#CBD5E1"
).pack(pady=(0, 35))

# ---------------- MAIN CONTENT ----------------

content = tk.Frame(root, bg=BG)
content.pack(side="right", fill="both", expand=True)


def clear_content():
    for widget in content.winfo_children():
        widget.destroy()


def page_heading(title, subtitle):
    tk.Label(
        content,
        text=title,
        font=("Arial", 25, "bold"),
        bg=BG,
        fg=TEXT
    ).pack(anchor="w", padx=35, pady=(30, 5))

    tk.Label(
        content,
        text=subtitle,
        font=("Arial", 12),
        bg=BG,
        fg=GREY
    ).pack(anchor="w", padx=35)


# ---------------- DASHBOARD ----------------

def show_dashboard():
    clear_content()

    subjects = get_subjects()
    records = get_attendance()

    total_classes = len(records)
    total_present = sum(1 for r in records if r[4] == "Present")

    percentage = (
        total_present / total_classes * 100
        if total_classes else 0
    )

    page_heading(
        "Dashboard",
        "Welcome to your smart attendance manager!"
    )

    card = tk.Frame(content, bg=WHITE, padx=25, pady=25)
    card.pack(fill="x", padx=35, pady=25)

    tk.Label(
        card,
        text="Welcome to AttendEase!",
        font=("Arial", 19, "bold"),
        bg=WHITE,
        fg=TEXT
    ).pack(anchor="w")

    tk.Label(
        card,
        text="Manage subjects, track attendance and stay above 75%.",
        font=("Arial", 11),
        bg=WHITE,
        fg=GREY
    ).pack(anchor="w", pady=10)

    stats = tk.Frame(content, bg=BG)
    stats.pack(fill="x", padx=35)

    cards = [
        ("TOTAL SUBJECTS", len(subjects)),
        ("CLASSES CONDUCTED", total_classes),
        ("CLASSES ATTENDED", total_present),
        ("OVERALL ATTENDANCE", f"{percentage:.1f}%")
    ]

    for heading, value in cards:
        box = tk.Frame(stats, bg=WHITE, padx=12, pady=20)
        box.pack(side="left", fill="both", expand=True, padx=5)

        tk.Label(
            box,
            text=heading,
            font=("Arial", 9, "bold"),
            bg=WHITE,
            fg=GREY
        ).pack()

        tk.Label(
            box,
            text=str(value),
            font=("Arial", 22, "bold"),
            bg=WHITE,
            fg=BLUE
        ).pack(pady=8)


# ---------------- MANAGE SUBJECTS ----------------

def show_subjects():
    clear_content()

    page_heading(
        "Manage Subjects",
        "Add and manage your college subjects."
    )

    form = tk.Frame(content, bg=WHITE, padx=20, pady=20)
    form.pack(fill="x", padx=35, pady=25)

    tk.Label(
        form,
        text="Subject Name",
        font=("Arial", 11, "bold"),
        bg=WHITE
    ).grid(row=0, column=0, sticky="w", padx=5)

    name_entry = tk.Entry(form, font=("Arial", 12), width=25)
    name_entry.grid(row=1, column=0, padx=5, pady=10)

    tk.Label(
        form,
        text="Subject Code",
        font=("Arial", 11, "bold"),
        bg=WHITE
    ).grid(row=0, column=1, sticky="w", padx=5)

    code_entry = tk.Entry(form, font=("Arial", 12), width=20)
    code_entry.grid(row=1, column=1, padx=5, pady=10)

    table_frame = tk.Frame(content, bg=BG)
    table_frame.pack(fill="both", expand=True, padx=35)

    tk.Label(
        table_frame,
        text="Your Subjects",
        font=("Arial", 16, "bold"),
        bg=BG,
        fg=TEXT
    ).pack(anchor="w", pady=(0, 12))

    table = ttk.Treeview(
        table_frame,
        columns=("name", "code"),
        show="headings",
        height=10
    )

    table.heading("name", text="Subject Name")
    table.heading("code", text="Subject Code")
    table.column("name", width=300)
    table.column("code", width=200)
    table.pack(fill="both", expand=True)

    def refresh_table():
        for item in table.get_children():
            table.delete(item)

        for subject_id, name, code in get_subjects():
            table.insert(
                "",
                "end",
                iid=str(subject_id),
                values=(name, code)
            )

    def add_subject():
        name = name_entry.get().strip()
        code = code_entry.get().strip().upper()

        if not name or not code:
            messagebox.showwarning(
                "Missing Information",
                "Please enter both subject name and code."
            )
            return

        if add_subject_to_db(name, code):
            name_entry.delete(0, tk.END)
            code_entry.delete(0, tk.END)
            refresh_table()

            messagebox.showinfo(
                "Success",
                "Subject saved successfully!"
            )
        else:
            messagebox.showerror(
                "Duplicate Code",
                "This subject code already exists."
            )

    def remove_subject():
        selected = table.selection()

        if not selected:
            messagebox.showwarning(
                "Select Subject",
                "Please select a subject to delete."
            )
            return

        confirm = messagebox.askyesno(
            "Confirm Deletion",
            "Deleting this subject will also delete its attendance records. Continue?"
        )

        if confirm:
            delete_subject_from_db(int(selected[0]))
            refresh_table()

            messagebox.showinfo(
                "Success",
                "Subject deleted successfully!"
            )

    tk.Button(
        form,
        text="Add Subject",
        font=("Arial", 11, "bold"),
        bg=BLUE,
        fg="white",
        relief="flat",
        padx=15,
        pady=8,
        command=add_subject
    ).grid(row=1, column=2, padx=15)

    tk.Button(
        table_frame,
        text="Delete Selected Subject",
        font=("Arial", 10, "bold"),
        bg=RED,
        fg="white",
        relief="flat",
        padx=12,
        pady=8,
        command=remove_subject
    ).pack(anchor="e", pady=12)

    refresh_table()


# ---------------- MARK ATTENDANCE ----------------

def show_attendance():
    clear_content()

    page_heading(
        "Mark Attendance",
        "Select a subject, date and attendance status."
    )

    subjects = get_subjects()

    form = tk.Frame(content, bg=WHITE, padx=20, pady=20)
    form.pack(fill="x", padx=35, pady=20)

    tk.Label(
        form,
        text="Select Subject",
        font=("Arial", 11, "bold"),
        bg=WHITE
    ).grid(row=0, column=0, sticky="w", padx=8)

    subject_options = {
        f"{name} ({code})": subject_id
        for subject_id, name, code in subjects
    }

    subject_box = ttk.Combobox(
        form,
        values=list(subject_options.keys()),
        state="readonly",
        width=25,
        font=("Arial", 11)
    )
    subject_box.grid(row=1, column=0, padx=8, pady=10)

    tk.Label(
        form,
        text="Class Date (YYYY-MM-DD)",
        font=("Arial", 11, "bold"),
        bg=WHITE
    ).grid(row=0, column=1, sticky="w", padx=8)

    date_entry = tk.Entry(form, font=("Arial", 11), width=18)
    date_entry.grid(row=1, column=1, padx=8, pady=10)
    date_entry.insert(0, date.today().isoformat())

    tk.Label(
        form,
        text="Attendance Status",
        font=("Arial", 11, "bold"),
        bg=WHITE
    ).grid(row=0, column=2, sticky="w", padx=8)

    status_var = tk.StringVar(value="Present")

    status_box = ttk.Combobox(
        form,
        textvariable=status_var,
        values=["Present", "Absent"],
        state="readonly",
        width=12,
        font=("Arial", 11)
    )
    status_box.grid(row=1, column=2, padx=8, pady=10)

    history_frame = tk.Frame(content, bg=BG)
    history_frame.pack(fill="both", expand=True, padx=35)

    tk.Label(
        history_frame,
        text="Attendance History",
        font=("Arial", 16, "bold"),
        bg=BG,
        fg=TEXT
    ).pack(anchor="w", pady=(0, 12))

    table = ttk.Treeview(
        history_frame,
        columns=("subject", "code", "date", "status"),
        show="headings",
        height=10
    )

    for col, heading in [
        ("subject", "Subject"),
        ("code", "Code"),
        ("date", "Class Date"),
        ("status", "Status")
    ]:
        table.heading(col, text=heading)

    table.column("subject", width=220)
    table.column("code", width=100)
    table.column("date", width=150)
    table.column("status", width=120)

    table.pack(fill="both", expand=True)

    def refresh_history():
        for item in table.get_children():
            table.delete(item)

        for record in get_attendance():
            record_id, name, code, class_date, status = record

            table.insert(
                "",
                "end",
                iid=str(record_id),
                values=(name, code, class_date, status)
            )

    def save_attendance():
        selected_subject = subject_box.get()
        class_date = date_entry.get().strip()
        status = status_var.get()

        if not selected_subject:
            messagebox.showwarning(
                "Select Subject",
                "Please select a subject first."
            )
            return

        try:
            date.fromisoformat(class_date)

            if class_date > date.today().isoformat():
                messagebox.showwarning(
                    "Invalid Date",
                    "You cannot mark attendance for a future date."
                )
                return

        except ValueError:
            messagebox.showerror(
                "Invalid Date",
                "Enter the date in YYYY-MM-DD format."
            )
            return

        subject_id = subject_options[selected_subject]

        mark_attendance(subject_id, class_date, status)
        refresh_history()

        messagebox.showinfo(
            "Success",
            "Attendance saved successfully!"
        )

    tk.Button(
        form,
        text="Save Attendance",
        font=("Arial", 11, "bold"),
        bg=BLUE,
        fg="white",
        relief="flat",
        padx=15,
        pady=9,
        command=save_attendance
    ).grid(row=1, column=3, padx=12)

    refresh_history()

    if not subjects:
        messagebox.showwarning(
            "No Subjects",
            "Please add subjects before marking attendance."
        )


# ---------------- ATTENDANCE CALCULATOR ----------------

def show_calculator():
    clear_content()

    page_heading(
        "Attendance Calculator",
        "Check your attendance percentage and 75% eligibility."
    )

    subjects = get_subjects()

    form = tk.Frame(content, bg=WHITE, padx=25, pady=25)
    form.pack(fill="x", padx=35, pady=30)

    tk.Label(
        form,
        text="Select Subject",
        font=("Arial", 12, "bold"),
        bg=WHITE
    ).pack(anchor="w")

    subject_options = {
        f"{name} ({code})": subject_id
        for subject_id, name, code in subjects
    }

    subject_box = ttk.Combobox(
        form,
        values=list(subject_options.keys()),
        state="readonly",
        width=35,
        font=("Arial", 12)
    )
    subject_box.pack(anchor="w", pady=12)

    result_frame = tk.Frame(content, bg=WHITE, padx=25, pady=25)
    result_frame.pack(fill="both", expand=True, padx=35)

    tk.Label(
        result_frame,
        text="Attendance Analysis",
        font=("Arial", 18, "bold"),
        bg=WHITE,
        fg=TEXT
    ).pack(anchor="w", pady=(0, 20))

    percentage_label = tk.Label(
        result_frame,
        text="-- %",
        font=("Arial", 32, "bold"),
        bg=WHITE,
        fg=BLUE
    )
    percentage_label.pack(anchor="w")

    progress = ttk.Progressbar(
        result_frame,
        length=450,
        maximum=100,
        mode="determinate"
    )
    progress.pack(anchor="w", pady=15)

    classes_label = tk.Label(
        result_frame,
        text="Classes attended: -- / --",
        font=("Arial", 12),
        bg=WHITE,
        fg=TEXT
    )
    classes_label.pack(anchor="w", pady=5)

    advice_label = tk.Label(
        result_frame,
        text="Select a subject and click Calculate.",
        font=("Arial", 12, "bold"),
        bg=WHITE,
        fg=GREY,
        justify="left",
        wraplength=700
    )
    advice_label.pack(anchor="w", pady=15)

    def calculate():
        selected = subject_box.get()

        if not selected:
            messagebox.showwarning(
                "Select Subject",
                "Please select a subject first."
            )
            return

        subject_id = subject_options[selected]
        total, present = get_attendance_stats(subject_id)

        if total == 0:
            percentage_label.config(text="0.0%", fg=BLUE)
            progress["value"] = 0
            classes_label.config(text="Classes attended: 0 / 0")
            advice_label.config(
                text="No attendance records found. Start marking attendance first.",
                fg=GREY
            )
            return

        percentage = (present / total) * 100

        percentage_label.config(
            text=f"{percentage:.2f}%",
            fg=GREEN if percentage >= TARGET else RED
        )

        progress["value"] = min(percentage, 100)

        classes_label.config(
            text=f"Classes attended: {present} / {total}"
        )

        if percentage >= TARGET:
            max_absences = math.floor(
                present / (TARGET / 100) - total + 1e-9
            )

            advice_label.config(
                text=(
                    f"Your attendance is above the required 75%.\n\n"
                    f"You can miss up to {max(0, max_absences)} "
                    f"consecutive classes and still maintain at least 75% attendance."
                ),
                fg=GREEN
            )
        else:
            target = TARGET / 100

            required = math.ceil(
                (target * total - present) / (1 - target) - 1e-9
            )

            advice_label.config(
                text=(
                    f"Your attendance is below the required 75%.\n\n"
                    f"You must attend the next {required} consecutive classes "
                    f"to reach at least 75% attendance."
                ),
                fg=RED
            )

    tk.Button(
        form,
        text="Calculate Attendance",
        font=("Arial", 11, "bold"),
        bg=BLUE,
        fg="white",
        relief="flat",
        padx=18,
        pady=10,
        command=calculate
    ).pack(anchor="w", pady=10)

    if not subjects:
        messagebox.showwarning(
            "No Subjects",
            "Please add a subject before using the calculator."
        )


# ---------------- REPORTS ----------------

def show_reports():
    clear_content()

    page_heading(
        "Attendance Reports",
        "View subject-wise statistics and export your records."
    )

    subjects = get_subjects()

    # Calculate subject-wise report data
    report_data = []

    for subject_id, name, code in subjects:
        total, present = get_attendance_stats(subject_id)
        absent = total - present

        percentage = (
            present / total * 100
            if total > 0 else 0
        )

        report_data.append({
            "name": name,
            "code": code,
            "total": total,
            "present": present,
            "absent": absent,
            "percentage": percentage
        })

    # Summary cards
    summary = tk.Frame(content, bg=BG)
    summary.pack(fill="x", padx=35, pady=20)

    total_subjects = len(subjects)
    total_classes = sum(item["total"] for item in report_data)
    total_present = sum(item["present"] for item in report_data)
    total_absent = sum(item["absent"] for item in report_data)

    overall = (
        total_present / total_classes * 100
        if total_classes > 0 else 0
    )

    summary_cards = [
        ("SUBJECTS", total_subjects),
        ("CLASSES", total_classes),
        ("PRESENT", total_present),
        ("OVERALL", f"{overall:.1f}%")
    ]

    for heading, value in summary_cards:
        card = tk.Frame(summary, bg=WHITE, padx=12, pady=15)
        card.pack(side="left", fill="both", expand=True, padx=5)

        tk.Label(
            card,
            text=heading,
            font=("Arial", 9, "bold"),
            bg=WHITE,
            fg=GREY
        ).pack()

        tk.Label(
            card,
            text=str(value),
            font=("Arial", 20, "bold"),
            bg=WHITE,
            fg=BLUE
        ).pack(pady=5)

    # Subject-wise table
    table_frame = tk.Frame(content, bg=BG)
    table_frame.pack(fill="both", expand=True, padx=35, pady=5)

    tk.Label(
        table_frame,
        text="Subject-wise Attendance Summary",
        font=("Arial", 16, "bold"),
        bg=BG,
        fg=TEXT
    ).pack(anchor="w", pady=(0, 10))

    columns = (
        "name", "code", "total",
        "present", "absent", "percentage"
    )

    table = ttk.Treeview(
        table_frame,
        columns=columns,
        show="headings",
        height=6
    )

    headings = {
        "name": "Subject",
        "code": "Code",
        "total": "Conducted",
        "present": "Present",
        "absent": "Absent",
        "percentage": "Attendance %"
    }

    for col, heading in headings.items():
        table.heading(col, text=heading)

    table.column("name", width=170)
    table.column("code", width=90)
    table.column("total", width=90)
    table.column("present", width=90)
    table.column("absent", width=90)
    table.column("percentage", width=120)

    table.pack(fill="x")

    table.tag_configure("low", foreground=RED)
    table.tag_configure("safe", foreground=GREEN)

    for item in report_data:
        tag = "safe" if item["percentage"] >= TARGET else "low"

        table.insert(
            "",
            "end",
            values=(
                item["name"],
                item["code"],
                item["total"],
                item["present"],
                item["absent"],
                f'{item["percentage"]:.2f}%'
            ),
            tags=(tag,)
        )

    # Low attendance warning
    low_subjects = [
        item["name"]
        for item in report_data
        if item["total"] > 0 and item["percentage"] < TARGET
    ]

    warning_text = (
        "Subjects below 75%: " + ", ".join(low_subjects)
        if low_subjects
        else "All subjects with attendance records are at or above 75%."
    )

    tk.Label(
        content,
        text=warning_text,
        font=("Arial", 10, "bold"),
        bg=BG,
        fg=RED if low_subjects else GREEN,
        wraplength=750,
        justify="left"
    ).pack(anchor="w", padx=35, pady=10)

    # Chart area
    chart_frame = tk.Frame(content, bg=WHITE, padx=15, pady=10)
    chart_frame.pack(fill="x", padx=35, pady=10)

    tk.Label(
        chart_frame,
        text="Subject Attendance Chart",
        font=("Arial", 14, "bold"),
        bg=WHITE,
        fg=TEXT
    ).pack(anchor="w", pady=(0, 5))

    chart = tk.Canvas(
        chart_frame,
        height=170,
        bg=WHITE,
        highlightthickness=0
    )
    chart.pack(fill="x", expand=True)

    def draw_chart(event=None):
        chart.delete("all")

        width = chart.winfo_width()

        if width < 100:
            return

        chart_height = 170
        left = 125
        right = width - 35
        usable_width = max(100, right - left)

        # Chart scale
        chart.create_line(
            left, 15, left, chart_height - 25,
            fill="#CBD5E1"
        )

        chart.create_line(
            left, chart_height - 25,
            right, chart_height - 25,
            fill="#CBD5E1"
        )

        for value in [0, 25, 50, 75, 100]:
            x = left + usable_width * value / 100

            chart.create_text(
                x,
                chart_height - 10,
                text=str(value),
                fill=GREY,
                font=("Arial", 8)
            )

        if not report_data:
            chart.create_text(
                width / 2,
                75,
                text="Add subjects to display the attendance chart.",
                fill=GREY,
                font=("Arial", 10)
            )
            return

        visible_items = report_data[:5]

        row_height = 26
        for index, item in enumerate(visible_items):
            y = 25 + index * row_height

            chart.create_text(
                left - 10,
                y + 7,
                text=item["code"],
                anchor="e",
                fill=TEXT,
                font=("Arial", 9)
            )

            bar_width = usable_width * min(
                item["percentage"], 100
            ) / 100

            color = (
                GREEN if item["percentage"] >= TARGET
                else RED
            )

            chart.create_rectangle(
                left,
                y,
                left + bar_width,
                y + 14,
                fill=color,
                outline=""
            )

            chart.create_text(
                min(left + bar_width + 28, right),
                y + 7,
                text=f'{item["percentage"]:.1f}%',
                fill=TEXT,
                font=("Arial", 8),
                anchor="w" if left + bar_width + 28 <= right else "e"
            )

        if len(report_data) > 5:
            chart.create_text(
                width - 5,
                chart_height - 30,
                text="Showing first 5 subjects",
                anchor="e",
                fill=GREY,
                font=("Arial", 8)
            )

    chart.bind("<Configure>", draw_chart)
    chart.after(100, draw_chart)

    # Export CSV
    def export_csv():
        records = get_attendance()

        if not records:
            messagebox.showwarning(
                "No Records",
                "There are no attendance records to export."
            )
            return

        file_path = filedialog.asksaveasfilename(
            title="Save Attendance Report",
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv")],
            initialfile="AttendEase_Attendance_Report.csv"
        )

        if not file_path:
            return

        try:
            with open(
                file_path,
                "w",
                newline="",
                encoding="utf-8-sig"
            ) as file:

                writer = csv.writer(file)

                writer.writerow([
                    "Subject",
                    "Subject Code",
                    "Class Date",
                    "Attendance Status"
                ])

                for record in records:
                    record_id, name, code, class_date, status = record

                    writer.writerow([
                        name,
                        code,
                        class_date,
                        status
                    ])

            messagebox.showinfo(
                "Export Successful",
                "Your attendance report has been exported successfully!"
            )

        except OSError as error:
            messagebox.showerror(
                "Export Error",
                f"Could not save the report:\n{error}"
            )

    button_frame = tk.Frame(content, bg=BG)
    button_frame.pack(fill="x", padx=35, pady=12)

    tk.Button(
        button_frame,
        text="Export Attendance to CSV",
        font=("Arial", 11, "bold"),
        bg=BLUE,
        fg="white",
        relief="flat",
        padx=18,
        pady=10,
        command=export_csv
    ).pack(side="left")

    tk.Label(
        button_frame,
        text=f"Attendance requirement: {TARGET}%",
        font=("Arial", 10, "bold"),
        bg=BG,
        fg=GREY
    ).pack(side="right")


# ---------------- NAVIGATION ----------------

pages = [
    ("Dashboard", show_dashboard),
    ("Manage Subjects", show_subjects),
    ("Mark Attendance", show_attendance),
    ("Attendance Calculator", show_calculator),
    ("Reports", show_reports)
]

for page_name, page_function in pages:
    tk.Button(
        sidebar,
        text=page_name,
        font=("Arial", 11),
        bg=SIDEBAR,
        fg="white",
        activebackground=BLUE,
        activeforeground="white",
        relief="flat",
        anchor="w",
        padx=25,
        pady=13,
        command=page_function
    ).pack(fill="x", padx=8, pady=3)


# ---------------- START APPLICATION ----------------

show_dashboard()

root.mainloop()