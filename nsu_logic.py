import re

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

# PREREQUISITE KNOWLEDGE BASE (Simplified for Demo)
PREREQUISITES = {
    "MIS210": ["MIS105"],
    "MIS310": ["MIS210"],
    "MIS320": ["MIS210"],
    "MIS470": ["MIS310", "MIS320"],
    "MAT120": ["MAT116"],
    "CSE215": ["CSE115"],
    "CSE225": ["CSE215"],
}


def check_prerequisites(course_code, passed_courses):
    """Returns True if student is ELIGIBLE to take the course."""
    if course_code not in PREREQUISITES:
        return True, "No Prereq"

    required = PREREQUISITES[course_code]
    missing = [req for req in required if req not in passed_courses]

    if missing:
        return False, f"Missing: {', '.join(missing)}"
    return True, "Eligible"


def calculate_cgpa(df):
    total_pts = 0
    total_cr = 0
    earned_cr = 0
    passed_courses = set()

    # Sort by semester to handle retakes chronologically (Logic v5.2)
    # For this demo, we use a simplified dictionary overwrite
    course_map = {}

    for _, row in df.iterrows():
        c = row["course_code"].strip()
        g = row["grade"].strip().upper()
        try:
            cr = float(row["credits"])
        except:
            cr = 0.0

        if g in GRADE_POINTS:
            course_map[c] = {"grade": g, "credits": cr, "pts": GRADE_POINTS[g]}
        elif g == "T":
            course_map[c] = {"grade": "T", "credits": cr, "pts": 0}

    for c, data in course_map.items():
        if data["grade"] != "T":
            total_pts += data["pts"] * data["credits"]
            total_cr += data["credits"]

        if data["grade"] not in ["F", "W"]:
            earned_cr += data["credits"]
            passed_courses.add(c)

    cgpa = total_pts / total_cr if total_cr > 0 else 0.0
    return cgpa, earned_cr, passed_courses


def suggest_courses(passed_courses, all_program_courses):
    """AI Advisor: Suggests courses the student is eligible for."""
    suggestions = []
    for course in all_program_courses:
        if course not in passed_courses:
            is_eligible, reason = check_prerequisites(course, passed_courses)
            if is_eligible:
                suggestions.append(course)
    return suggestions
