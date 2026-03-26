#!/usr/bin/env python3
import csv
import sys
import re
from datetime import date


# --- 1. VISUAL SETUP ---
class Color:
    HEADER = "\033[95m"
    BLUE = "\033[94m"
    CYAN = "\033[96m"
    GREEN = "\033[92m"
    WARNING = "\033[93m"
    FAIL = "\033[91m"
    END = "\033[0m"
    BOLD = "\033[1m"


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
    today = date.today().strftime("%Y-%m-%d")
    print(f"\n{Color.BLUE}{'='*60}{Color.END}")
    print(
        f"{Color.BOLD}NSU DEGREE AUDIT SYSTEM (v7.0 - TRANSPARENT RETAKE EDITION){Color.END}"
    )
    print(f"Student Record: {Color.BOLD}Mushfiq Rahman{Color.END} ({filename})")
    print(f"Program:        {Color.BOLD}BSC in CSE{Color.END}")
    print(f"Date:           {today}")
    print(f"{Color.BLUE}{'='*60}{Color.END}")


def load_requirements(program_file):
    requirements = {}
    current_category = None
    try:
        with open(program_file, "r") as file:
            for line in file:
                line = line.strip()
                if line.startswith("##"):
                    header_text = line.replace("##", "").strip()
                    if "Program:" in header_text:
                        current_category = None
                        continue
                    match = re.search(r"\(.*(\d+).*\)", header_text)
                    if match:
                        needed_count = int(match.group(1))
                        clean_name = header_text.split("(")[0].strip()
                    else:
                        needed_count = None
                        clean_name = header_text
                    current_category = clean_name
                    requirements[current_category] = {
                        "courses": [],
                        "needed": needed_count,
                    }
                elif line.startswith("-") and current_category:
                    clean_line = line.replace("-", "").replace("*", "").strip()
                    course = (
                        clean_line.split(":")[0].strip()
                        if ":" in clean_line
                        else clean_line
                    )
                    if course and course not in [
                        "Degree",
                        "Total Credits Required",
                        "*Any Department*",
                    ]:
                        requirements[current_category]["courses"].append(course)
    except FileNotFoundError:
        print(f"{Color.FAIL}Error: Program file '{program_file}' not found.{Color.END}")
        sys.exit(1)
    return requirements


def audit_student(transcript_file, program_file):
    print_header(transcript_file)

    # --- STEP 0: WAIVER INPUT ---
    waivers = set()
    print(f"\n{Color.HEADER}[Admin Input Required]{Color.END}")
    print("Enter course codes to WAIVE (e.g., ENG102). Press Enter to finish.")
    while True:
        course_input = input(f"Waiver > ").strip().upper()
        if not course_input:
            break
        waivers.add(course_input)
        print(f"   -> {Color.WARNING}{course_input} marked as WAIVED{Color.END}")

    # --- STEP 1: Process Transcript & Track History ---
    completed_courses = {}
    invalid_courses = []

    try:
        with open(transcript_file, mode="r") as file:
            reader = csv.DictReader(file)
            for row in reader:
                course = row["Course"].strip()
                grade = row["Grade"].strip().upper()
                try:
                    cr = float(row["Credits"])
                except:
                    cr = 0.0

                # Data Integrity Check
                if not re.match(
                    r"^[A-Za-z]{3}\d{3}[A-Za-z]?$", course
                ) and grade not in ["W", "I"]:
                    invalid_courses.append((course, grade, cr))
                    continue

                # Initialize course in tracking dictionary if not exists
                if course not in completed_courses:
                    completed_courses[course] = {
                        "attempts": [],
                        "best_grade": None,
                        "credits": cr,
                    }

                # Record this attempt in history
                completed_courses[course]["attempts"].append(grade)

                # Determine the mathematically highest grade to keep for the audit
                current_best = completed_courses[course]["best_grade"]

                if grade in GRADE_POINTS:
                    if current_best not in GRADE_POINTS or GRADE_POINTS[
                        grade
                    ] > GRADE_POINTS.get(current_best, -1):
                        completed_courses[course]["best_grade"] = grade
                elif grade == "T" and current_best not in GRADE_POINTS:
                    completed_courses[course]["best_grade"] = "T"
                elif grade == "W" and current_best is None:
                    completed_courses[course]["best_grade"] = "W"

    except FileNotFoundError:
        print(
            f"{Color.FAIL}Error: Transcript '{transcript_file}' not found.{Color.END}"
        )
        return

    if invalid_courses:
        print(
            f"\n{Color.FAIL}🚨 [DATA INTEGRITY WARNING] UNIDENTIFIED COURSES DETECTED 🚨{Color.END}"
        )
        for inv_c, inv_g, inv_cr in invalid_courses:
            print(
                f"  -> {Color.WARNING}{inv_c}{Color.END} (Grade: {inv_g}, Cr: {inv_cr})"
            )

    # --- STEP 2: Course Breakdown ---
    print(f"\n{Color.HEADER}--- Course Breakdown & Retake History ---{Color.END}")
    print(
        f"{Color.BOLD}{'COURSE':<10} {'ATTEMPT HISTORY':<20} {'FINAL GRADE':<12} {'CREDITS':<10} {'POINTS':<10}{Color.END}"
    )
    print("-" * 65)

    total_points = 0
    total_gpa_credits = 0
    total_earned_credits = 0

    for course, data in sorted(completed_courses.items()):
        best_grade = data["best_grade"]
        credits = data["credits"]
        attempts = data["attempts"]

        # Create the visual history string (e.g., "F -> D -> B")
        history_str = " ➔ ".join(attempts) if len(attempts) > 1 else ""
        if history_str:
            history_str = f"{Color.WARNING}{history_str}{Color.END}"

        if best_grade in GRADE_POINTS:
            points = GRADE_POINTS[best_grade]
            quality_points = points * credits
            grade_color = Color.GREEN if best_grade not in ["F", "D"] else Color.FAIL

            print(
                f"{course:<10} {history_str:<29} {grade_color}{best_grade:<12}{Color.END} {credits:<10} {quality_points:<10.1f}"
            )

            total_points += quality_points
            total_gpa_credits += credits
            total_earned_credits += credits

        elif best_grade == "T":
            print(
                f"{course:<10} {history_str:<29} {Color.CYAN}{best_grade:<12}{Color.END} {credits:<10} {'---':<10}"
            )
            total_earned_credits += credits

        elif best_grade == "W":
            print(
                f"{course:<10} {history_str:<29} {Color.WARNING}{best_grade:<12}{Color.END} {'0.0':<10} {'0.0':<10}"
            )

    print("-" * 65)
    cgpa = total_points / total_gpa_credits if total_gpa_credits > 0 else 0.0
    cgpa_color = Color.GREEN if cgpa >= 2.0 else Color.FAIL
    print(f"Total Earned Credits: {total_earned_credits}")
    print(f"Current CGPA:         {cgpa_color}{cgpa:.2f}{Color.END}")

    is_probation = False
    if cgpa < 2.0:
        is_probation = True
        print(f"\n{Color.FAIL}⚠️  STATUS: PROBATION (CGPA < 2.0){Color.END}")
    else:
        print(f"\n{Color.GREEN}✅  STATUS: Good Standing{Color.END}")

    # --- STEP 3: Check Requirements ---
    requirements = load_requirements(program_file)
    print(f"\n{Color.HEADER}--- Deficiency Report ---{Color.END}")

    failure_reasons = []
    if is_probation:
        failure_reasons.append("CGPA is below 2.0 (Probation Status)")

    overall_missing = False
    used_courses = set()

    for category, data in requirements.items():
        if "Free Electives" in category:
            continue

        required_courses = data["courses"]
        needed_count = data["needed"]

        passed = []
        for c in required_courses:
            is_taken = c in completed_courses and (
                completed_courses[c]["best_grade"] in GRADE_POINTS
                or completed_courses[c]["best_grade"] == "T"
            )
            is_waived = c in waivers

            if is_taken:
                passed.append(c)
                used_courses.add(c)
            elif is_waived:
                passed.append(c)

        cat_display = f"{Color.BLUE}[{category}]{Color.END}"

        if needed_count:
            if len(passed) < needed_count:
                overall_missing = True
                missing = needed_count - len(passed)
                print(
                    f"{cat_display} {Color.WARNING}Found {len(passed)}/{needed_count}. Need {missing} more.{Color.END}"
                )
                failure_reasons.append(f"Missing {missing} course(s) from {category}")
        else:
            missing = [c for c in required_courses if c not in passed]
            if missing:
                overall_missing = True
                print(
                    f"{cat_display} {Color.FAIL}Missing: {', '.join(missing)}{Color.END}"
                )
                failure_reasons.append(f"Missing Mandatory: {', '.join(missing)}")

    forbidden_electives = ["ENG102", "BUS112"]
    free_electives = []

    for c in completed_courses:
        grade = completed_courses[c]["best_grade"]
        if (grade in GRADE_POINTS or grade == "T") and grade not in ["F", "W"]:
            if c not in used_courses and c not in forbidden_electives:
                free_electives.append(c)

    FE_NEEDED = 3
    cat_display = f"{Color.BLUE}[Free Electives]{Color.END}"

    if len(free_electives) >= FE_NEEDED:
        pass
    else:
        overall_missing = True
        missing = FE_NEEDED - len(free_electives)
        print(
            f"{cat_display} {Color.WARNING}Found {len(free_electives)}/{FE_NEEDED} ({', '.join(free_electives)}). Need {missing} more.{Color.END}"
        )
        failure_reasons.append(f"Missing {missing} Free Elective(s)")

    print(f"\n{Color.BLUE}{'='*60}{Color.END}")
    if not overall_missing and not is_probation:
        print(f"{Color.GREEN}🎉  GRADUATION ELIGIBLE: All requirements met!{Color.END}")
    else:
        print(f"{Color.FAIL}❌  Result: NOT Eligible for Graduation.{Color.END}")
        for reason in failure_reasons:
            print(f" - {Color.FAIL}{reason}{Color.END}")

    print(f"{Color.BLUE}{'='*60}{Color.END}\n")


if __name__ == "__main__":
    t_file = sys.argv[1] if len(sys.argv) > 1 else "TC_Advanced_Retakes.csv"
    p_file = sys.argv[2] if len(sys.argv) > 2 else "cseprogram.md"
    audit_student(t_file, p_file)
