import csv
import sys


def audit_level_1(transcript_file):
    """
    LEVEL 1: CREDIT TALLY ENGINE
    Goal: Calculate total 'Earned Credits' for graduation.

    Logic:
    1. Pass Grades (A to D): Count as earned credits.
    2. Fail/Withdraw (F, W, I): Do NOT count.
    3. Retakes: If a student passes a course multiple times (e.g., to improve grade),
       or fails then passes, the credit is counted ONLY ONCE.
    """
    print(f"--- LEVEL 1 AUDIT: {transcript_file} ---")

    earned_credits = 0.0
    passed_courses = set()  # We use a set to track courses we have already counted

    try:
        with open(transcript_file, mode="r") as file:
            reader = csv.DictReader(file)

            for row in reader:
                course = row["Course"].strip()
                grade = row["Grade"].strip().upper()

                # Handle potential empty credit values safely
                try:
                    credits = float(row["Credits"])
                except ValueError:
                    credits = 0.0

                # --- THE LOGIC GATE ---

                # 1. Ignore Non-Earning Grades immediately
                if grade in ["F", "W", "I"]:
                    # print(f"Skipped {course} ({grade}): No credit.")
                    continue

                # 2. Check for Duplicate Credits (Retakes)
                # If we have already seen this course in our 'passed' set, ignore it.
                if course in passed_courses:
                    # print(f"Skipped {course} ({grade}): Credits already counted.")
                    continue

                # 3. Add Valid Credits
                earned_credits += credits
                passed_courses.add(course)
                print(f"✓ Counted: {course} ({credits} Cr) - Grade: {grade}")

        print("-" * 30)
        print(f"TOTAL VALID CREDITS EARNED: {earned_credits}")
        print("-" * 30)

    except FileNotFoundError:
        print(f"Error: File '{transcript_file}' not found.")
    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    # If a filename is provided in terminal, use it. Otherwise default to test_L1.csv
    filename = sys.argv[1] if len(sys.argv) > 1 else "test_L1.csv"
    audit_level_1(filename)
