import hashlib
import getpass
import sys
import os


class Color:
    BLUE = "\033[94m"
    GREEN = "\033[92m"
    FAIL = "\033[91m"
    END = "\033[0m"
    BOLD = "\033[1m"


# Simulated secure database of hashed passwords
# In reality, this would query an SQL Database or LDAP
USER_DB = {
    "admin": hashlib.sha256("nsu123".encode()).hexdigest(),
    "nabeel": hashlib.sha256("prof123".encode()).hexdigest(),
    "mushfiq": hashlib.sha256("student123".encode()).hexdigest(),
}

ROLES = {"admin": "Super User", "nabeel": "Professor / Advisor", "mushfiq": "Student"}


def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")


def require_login():
    clear_screen()
    print(f"{Color.BLUE}{'='*50}{Color.END}")
    print(f"{Color.BOLD}   NORTH SOUTH UNIVERSITY - MCP TERMINAL LOGIN{Color.END}")
    print(f"{Color.BLUE}{'='*50}{Color.END}")
    print("Authorized Personnel Only.\n")

    attempts = 3
    while attempts > 0:
        username = input("Username: ").strip().lower()
        # getpass hides the typing (like real terminal logins)
        password = getpass.getpass("Password: ")

        hashed_attempt = hashlib.sha256(password.encode()).hexdigest()

        if username in USER_DB and USER_DB[username] == hashed_attempt:
            clear_screen()
            role = ROLES[username]
            print(f"{Color.GREEN}✅ Authentication Successful.{Color.END}")
            print(f"Logged in as: {Color.BOLD}{username.upper()}{Color.END} [{role}]\n")
            return username, role
        else:
            attempts -= 1
            print(
                f"{Color.FAIL}❌ Invalid credentials. Attempts remaining: {attempts}{Color.END}\n"
            )

    print(
        f"{Color.FAIL}SECURITY LOCKOUT: Too many failed attempts. Exiting.{Color.END}"
    )
    sys.exit(1)
