import os
import csv


def create_csv(filename, data):
    with open(filename, mode="w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["Semester", "Course", "Credits", "Grade"])
        writer.writerows(data)
    print(f"Created: {filename}")


# Create directory
os.makedirs("test_cases", exist_ok=True)

# TC10 & TC24: The Retake & Withdrawal File
create_csv(
    "test_cases/TC_Retakes.csv",
    [
        ["Spring", "MAT112", 3.0, "F"],
        ["Spring", "MIS105", 3.0, "W"],
        ["Summer", "MAT112", 3.0, "A"],
        ["Fall", "MIS105", 3.0, "B+"],
        ["Fall", "ENG102", 3.0, "C"],
        ["Spring2", "ENG102", 3.0, "A-"],
    ],
)

# TC35 & TC36: The Probation File (All courses taken, but GPA low)
create_csv(
    "test_cases/TC_Probation.csv",
    [
        ["Fall", "MIS105", 3.0, "D"],
        ["Fall", "ECO101", 3.0, "C-"],
        ["Spring", "ACT201", 3.0, "D+"],
        ["Spring", "MGT210", 3.0, "D"],
    ],
)

# TC38 & TC39: The Transfer File
create_csv(
    "test_cases/TC_Transfer.csv",
    [
        ["Transfer", "ENG102", 3.0, "T"],
        ["Transfer", "ECO101", 3.0, "T"],
        ["Transfer", "MAT112", 3.0, "T"],
        ["Fall", "MIS105", 3.0, "A"],
        ["Fall", "BUS112", 3.0, "A-"],
    ],
)

# TC41 & TC44: Free Elective Blacklist & Overflow
create_csv(
    "test_cases/TC_FreeElectives.csv",
    [
        ["Fall", "HIS101", 3.0, "A"],
        ["Fall", "HIS102", 3.0, "A"],
        [
            "Spring",
            "HIS103",
            3.0,
            "B+",
        ],  # This 3rd history should overflow to Free Electives
        [
            "Spring",
            "ENG102",
            3.0,
            "A",
        ],  # This should be blacklisted from Free Electives
        ["Summer", "MKT202", 3.0, "A"],
    ],
)

print("✅ Automated Test Case Generation Complete!")
