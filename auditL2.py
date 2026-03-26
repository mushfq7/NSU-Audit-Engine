#!/usr/bin/env python3
import csv
import sys
from datetime import date


# --- 1. SETUP COLORS ---
# We use ANSI codes to color the terminal text
class Color:
    HEADER = "\033[95m"
    BLUE = "\033[94m"
    GREEN = "\033[92m"  # Good stuff
    WARNING = "\033[93m"  # Waivers/Warnings
    FAIL = "\033[91m"  # Errors/Failures
    END = "\033[0m"  # Reset to normal
    BOLD = "\033[1m"


# NSU Grading Scale
GRADE_POINTS = {
    "A": 4.0,
    "A-": 3.7,
    "B+": 3.3,
    "B": 3.0,
    "B-": 2.7,
    "C+": 2.3,
    "C": 2.0,
    "C-": 1.7,
    "D+": 1.3,
    "D": 1.0,
    "F": 0.0,
}


def print_header(filename):
    """Prints the professional NSU-style header."""
    today = date.today().strftime("%Y-%m-%d")
    print(f"{Color.BLUE}{'='*60}{Color.END}")
    print(f"{Color.BOLD}NSU DEGREE AUDIT SYSTEM (v2.0){Color.END}")
    print(f"Student Record: {Color.BOLD}Mushfiq Rahman{Color.END} ({filename})")
    print(f"Program:        {Color.BOLD}BBA in MIS{Color.END}")
    print(f"Date:           {today}")
    print(f"{Color.BLUE}{'='*60}{Color.END}")


def audit_level_2(transcript_file):
    print_header(transcript_file)

    # --- INTERACTIVE WAIVER CHECK ---
    waivers = set()
    print(f"\n{Color.HEADER}[Admin Input Required]{Color.END}")
    print("Enter course codes to WAIVE (e.g., ENG102). Press Enter to finish.")
    while True:
        course_input = input(f"Waiver > ").strip().upper()
        if not course_input:
            break
        waivers.add(course_input)
        print(f"   -> {Color.WARNING}{course_input} marked as WAIVED.{Color.END}")

    course_history = {}

    try:
        with open(transcript_file, mode="r") as file:
            reader = csv.DictReader(file)

            for row in reader:
                course = row["Course"].strip()
                grade = row["Grade"].strip().upper()
                try:
                    credits = float(row["Credits"])
                except ValueError:
                    credits = 0.0

                if course in waivers:
                    continue
                if grade not in GRADE_POINTS:
                    continue

                points = GRADE_POINTS[grade]
                course_history[course] = {
                    "credits": credits,
                    "quality_points": points * credits,
                    "grade": grade,
                }

        # --- CALCULATE & PRINT ALIGNED TABLE ---
        total_attempted = 0
        total_quality_points = 0

        print("\n" + "-" * 45)
        # 3. ALIGNED TABLE HEADERS
        # {:<10} means "align left, 10 spaces wide"
        print(
            f"{Color.BOLD}{'COURSE':<10} {'GRADE':<8} {'CREDITS':<10} {'POINTS':<10}{Color.END}"
        )
        print("-" * 45)

        for course, data in course_history.items():
            g = data["grade"]
            pts = data["quality_points"]
            cr = data["credits"]

            # Dynamic coloring for grades
            grade_color = (
                Color.GREEN
                if getattr(data, "grade", "C") not in ["F", "D"]
                else Color.FAIL
            )

            # 3. ALIGNED ROW DATA
            print(f"{course:<10} {grade_color}{g:<8}{Color.END} {cr:<10} {pts:<10.1f}")

            total_attempted += cr
            total_quality_points += pts

        if total_attempted > 0:
            cgpa = total_quality_points / total_attempted
        else:
            cgpa = 0.0

        # CGPA Coloring
        cgpa_color = Color.GREEN if cgpa >= 2.0 else Color.FAIL

        print("-" * 45)
        print(f"Total Quality Points: {total_quality_points}")
        print(f"Total CGPA Credits:   {total_attempted}")
        print(f"{Color.BOLD}CALCULATED CGPA:      {cgpa_color}{cgpa:.2f}{Color.END}")
        print("-" * 45)

    except FileNotFoundError:
        print(f"{Color.FAIL}Error: File '{transcript_file}' not found.{Color.END}")


if __name__ == "__main__":
    filename = sys.argv[1] if len(sys.argv) > 1 else "test_L2.csv"
    audit_level_2(filename)
