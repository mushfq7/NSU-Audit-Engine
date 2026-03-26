import pytesseract
from PIL import Image
import sys
import os
import re
import csv


class Color:
    BLUE = "\033[94m"
    GREEN = "\033[92m"
    WARNING = "\033[93m"
    FAIL = "\033[91m"
    END = "\033[0m"


def parse_to_csv(raw_text, output_filename="scanned_transcript.csv"):
    """Parses chaotic OCR text into a structured academic CSV."""
    print(f"{Color.BLUE}Initializing Regex Parser Engine...{Color.END}")

    lines = raw_text.split("\n")
    current_semester = "Unknown Semester"
    parsed_data = []

    # Dictionary to fix common Tesseract OCR visual mistakes
    ocr_fixes = {
        "Az": "A-",  # OCR often reads A- as Az
        "CS": "C+",  # OCR often reads C+ as CS
        "]": "1",  # OCR often reads 1 as ] at the end of course codes
    }

    for line in lines:
        line = line.strip()
        if not line:
            continue

        # 1. Detect Semester Block (e.g., "Spring 2021", "Fall 2022")
        sem_match = re.search(
            r"(Spring|Summer|Fall|Intersession)\s+(\d{4})", line, re.IGNORECASE
        )
        if sem_match:
            current_semester = f"{sem_match.group(1).capitalize()} {sem_match.group(2)}"
            continue

        # 2. Detect Course Codes (Looks for 3 letters, optional space, 3 numbers/symbols)
        course_match = re.search(r"([A-Z]{3})\s*(\d{2}[\d\]])", line)
        if course_match:
            dept = course_match.group(1)
            num = course_match.group(2).replace("]", "1")
            course_code = f"{dept}{num}"

            # 3. Detect Grade
            grade_match = re.search(
                r"\b(A-|A|B\+|B-|B|C\+|C-|C|D\+|D|F|W|Az|CS)\b", line
            )
            grade = grade_match.group(1) if grade_match else None

            # 4. Detect Credits
            credit_match = re.search(r"\b([1-4]\.0)\b", line)
            credits = credit_match.group(1) if credit_match else "3.0"

            if grade:
                if grade in ocr_fixes:
                    grade = ocr_fixes[grade]
                parsed_data.append([current_semester, course_code, credits, grade])
                print(
                    f"  -> Extracted: {course_code:<8} | {credits} Cr | Grade: {grade:<2} | ({current_semester})"
                )

    # Save to CSV
    if parsed_data:
        with open(output_filename, mode="w", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(["Semester", "Course", "Credits", "Grade"])
            writer.writerows(parsed_data)
        print(
            f"\n{Color.GREEN}✅ Successfully parsed {len(parsed_data)} courses into {output_filename}{Color.END}"
        )
        return output_filename
    else:
        print(
            f"\n{Color.WARNING}⚠️ Regex Parser could not find any valid courses in the text.{Color.END}"
        )
        return None


def scan_image(image_path):
    if not os.path.exists(image_path):
        print(f"{Color.FAIL}Error: Could not find image at '{image_path}'{Color.END}")
        return None

    try:
        print(f"{Color.BLUE}Scanning Image: {image_path}...{Color.END}\n")
        img = Image.open(image_path)
        raw_text = pytesseract.image_to_string(img)
        return parse_to_csv(raw_text)

    except Exception as e:
        print(f"{Color.FAIL}OCR Engine Failed: {e}{Color.END}")
        return None


if __name__ == "__main__":
    if len(sys.argv) > 1:
        target_image = sys.argv[1]
    else:
        target_image = input("Enter the filename of the transcript image: ")

    scan_image(target_image)
