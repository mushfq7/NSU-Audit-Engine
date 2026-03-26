#!/usr/bin/env python3
# cli.py - The Main Terminal Application Controller
import sys
import os
import subprocess
import auth  # This imports the auth.py file


class Color:
    BLUE = "\033[94m"
    CYAN = "\033[96m"
    GREEN = "\033[92m"
    WARNING = "\033[93m"
    FAIL = "\033[91m"
    END = "\033[0m"
    BOLD = "\033[1m"


def print_menu(role):
    """Displays the interactive MCP menu based on the user's role."""
    print(f"\n{Color.CYAN}--- MCP Audit Control Panel ---{Color.END}")
    print("1. Run Level 1 Audit (Credit Tally)")
    print("2. Run Level 2 Audit (GPA Calculation)")
    print("3. Run BBA MIS Final Audit (testbba_L3.csv)")
    print("4. Run BSC CSE Final Audit (testcse_L3.csv)")
    print("5. Logout / Exit")

    # Conditional Rendering based on Role
    if role in ["Super User", "Professor / Advisor"]:
        print(f"\n{Color.WARNING}[Admin Tools & Edge Cases]{Color.END}")
        print("6. Run Forensic Scan (Catch Unidentified Courses in CSE)")
        print("7. Run Advanced Retake Analysis (MIS)")
        print("8. Run Transfer Student Scenario (MIS)")
        print("9. Run Major Change Scenario (MIS)")
        print("10. Launch NSU Student Portal (Streamlit Web App)")


def run_script(script_name, *args):
    """Executes a Python script as an external process."""
    command = [sys.executable, script_name] + list(args)
    try:
        print(f"\n{Color.BLUE}Executing: {' '.join(command)}{Color.END}\n")
        subprocess.run(command, check=True)
        input(
            f"\n{Color.GREEN}Process completed. Press Enter to return to menu...{Color.END}"
        )
        os.system("cls" if os.name == "nt" else "clear")
    except subprocess.CalledProcessError:
        print(
            f"\n{Color.FAIL}Error: The audit script crashed or returned an error.{Color.END}"
        )
        input("\nPress Enter to continue...")
    except FileNotFoundError:
        print(
            f"\n{Color.FAIL}Error: Python or the script '{script_name}' was not found.{Color.END}"
        )
        input("\nPress Enter to continue...")


def main():
    # 1. Force Secure Login before anything else
    username, role = auth.require_login()

    # 2. Start the Interactive Loop
    while True:
        print_menu(role)
        choice = input(f"\n{username}@nsu-mcp > ").strip()

        # Basic Commands (Available to all)
        if choice == "1":
            run_script("auditL1.py")
        elif choice == "2":
            run_script("auditL2.py")
        elif choice == "3":
            run_script("auditL3mis.py", "testbba_L3.csv", "misprogram.md")
        elif choice == "4":
            run_script("auditL3cse.py", "testcse_L3.csv", "cseprogram.md")
        elif choice == "5":
            print("\nLogging out safely...")
            sys.exit(0)

        # Admin Only Commands
        elif role in ["Super User", "Professor / Advisor"]:
            if choice == "6":
                run_script("auditL3cse.py", "testcse_L3.csv", "cseprogram.md")
            elif choice == "7":
                run_script("auditL3mis.py", "TC_Advanced_Retakes.csv", "misprogram.md")
            elif choice == "8":
                run_script("auditL3mis.py", "test_transfer.csv", "misprogram.md")
            elif choice == "9":
                run_script("auditL3mis.py", "test_major_change.csv", "misprogram.md")
            elif choice == "10":
                run_script("-m", "streamlit", "run", "main.py")
            else:
                print(f"\n{Color.WARNING}Invalid command.{Color.END}")
                input("Press Enter to continue...")
                os.system("cls" if os.name == "nt" else "clear")
        else:
            print(
                f"\n{Color.WARNING}Invalid command or insufficient permissions.{Color.END}"
            )
            input("Press Enter to continue...")
            os.system("cls" if os.name == "nt" else "clear")


if __name__ == "__main__":
    main()
