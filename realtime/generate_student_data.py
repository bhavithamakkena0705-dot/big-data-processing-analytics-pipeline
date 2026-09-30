
import csv
import random
import time
from pathlib import Path

output_file = Path("/content/big_data_project/realtime/input/student_stream.csv")

students = [
    ("ST001", "CSE", 3, "Big Data"),
    ("ST002", "CSE", 3, "Big Data"),
    ("ST003", "ECE", 3, "Cloud Computing"),
    ("ST004", "CSE", 3, "Cloud Computing"),
    ("ST005", "ECE", 3, "Big Data"),
    ("ST006", "CSE", 3, "Python"),
    ("ST007", "ECE", 3, "Python"),
    ("ST008", "CSE", 3, "Big Data")
]

if not output_file.exists():
    with open(output_file, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([
            "Student_ID", "Branch", "Year",
            "Subject", "Marks", "Attendance"
        ])

while True:
    student = random.choice(students)
    marks = random.randint(35, 98)
    attendance = random.randint(50, 99)

    with open(output_file, "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([
            student[0],
            student[1],
            student[2],
            student[3],
            marks,
            attendance
        ])

    print(
        f"New Record: {student[0]} | "
        f"{student[3]} | Marks: {marks} | "
        f"Attendance: {attendance}"
    )

    time.sleep(3)
