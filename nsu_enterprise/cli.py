import sys
import os
import auth

# Import your actual audit scripts here (assuming they are in the same folder)
# We use subprocess to run them cleanly as separate processes
import subprocess


class Color:
    BLUE = "\033[94m"
    CYAN = "\033[96m"
    GREEN = "\033[92m"
    WARNING = "\033[93m"
    END = "\033[0m"
    BOLD = "\033[1m"


def print_menu(role):
    print(f"{Color.CYAN}--- MCP Audit Control Panel ---{Color.END}")
    print("1. Run BBA MIS Audit (testbba_L3.csv)")
    print("2. Run BSC CSE Audit (testcse_L3.csv)")
    print("3. Run Advanced Retake Analysis")
    print("4. Logout / Exit")

    if role in ["Super User", "Professor / Advisor"]:
        print(f"\n{Color.WARNING}[Admin Tools]{Color.END}")
        print("5. Run Forensic Data Integrity Scan (Catch Unidentified Courses)")


def run_script(script_name, *args):
    """Executes a Python script as an external process (MCP style)."""
    command = [sys.executable, script_name] + list(args)
    try:
        print(f"\n{Color.BLUE}Executing: {' '.join(command)}{Color.END}\n")
        subprocess.run(command, check=True)
        input(
            f"\n{Color.GREEN}Process completed. Press Enter to return to menu...{Color.END}"
        )
        os.system("cls" if os.name == "nt" else "clear")
    except subprocess.CalledProcessError:
        print(f"\n{Color.FAIL}Error executing audit script.{Color.END}")
        input("\nPress Enter to continue...")
    except FileNotFoundError:
        print(
            f"\n{Color.FAIL}Error: Script '{script_name}' not found in current directory.{Color.END}"
        )
        input("\nPress Enter to continue...")


def main():
    # 1. Force Secure Login
    username, role = auth.require_login()

    # 2. Interactive Loop
    while True:
        print_menu(role)
        choice = input(f"\n{username}@nsu-mcp > ")

        if choice == "1":
            run_script("auditL3mis.py", "testbba_L3.csv", "misprogram.md")
        elif choice == "2":
            run_script("auditL3cse.py", "testcse_L3.csv", "cseprogram.md")
        elif choice == "3":
            run_script("auditL3mis.py", "TC_Advanced_Retakes.csv", "misprogram.md")
        elif choice == "4":
            print("Logging out safely...")
            sys.exit(0)
        elif choice == "5" and role in ["Super User", "Professor / Advisor"]:
            # Example of running the MIS script with CSE data to trigger the forensic errors
            run_script("auditL3mis.py", "testcse_L3.csv", "misprogram.md")
        else:
            print(
                f"{Color.WARNING}Invalid command or insufficient permissions.{Color.END}"
            )


if __name__ == "__main__":
    main()
