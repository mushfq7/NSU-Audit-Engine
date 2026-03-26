#!/usr/bin/env python3
# auth.py - The Security Layer & Identity Simulator
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


# Simulated Secure Database
# Passwords must be hashed. For this example:
# "admin123" -> 8c6976e5b5410415bde908bd4dee15dfb167a9c873fc4bb8a81f6f2ab448a918
# "student123" -> c3e9860b2eb2d1f76dfd2570b67df9cc66ef36cd66092782e4e7c7a52e9a3b60
# "prof123" -> 31cf0427845f7cddba109e2cf94819779df3073f1d3e85e1ba091c53f0d46dcb
USER_DB = {
    "admin": "8c6976e5b5410415bde908bd4dee15dfb167a9c873fc4bb8a81f6f2ab448a918",
    "mushfiq": "c3e9860b2eb2d1f76dfd2570b67df9cc66ef36cd66092782e4e7c7a52e9a3b60",
    "dr.nabeel": "31cf0427845f7cddba109e2cf94819779df3073f1d3e85e1ba091c53f0d46dcb",
}

ROLES = {
    "admin": "Super User",
    "mushfiq": "Student",
    "dr.nabeel": "Professor / Advisor",
}


def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")


def require_login():
    """Forces the user to login and returns their username and role."""
    clear_screen()
    print(f"\n{Color.BLUE}{'='*60}{Color.END}")
    print(
        f"{Color.BOLD} NORTH SOUTH UNIVERSITY - MCP TERMINAL LOGIN (LOCAL){Color.END}"
    )
    print(f"{Color.BLUE}{'='*60}{Color.END}")
    print("Authorized Personnel Only.\n")

    attempts = 3
    while attempts > 0:
        username = input("Username: ").strip().lower()
        password = getpass.getpass("Password: ")

        hashed_attempt = hashlib.sha256(password.encode()).hexdigest()

        if username in USER_DB and USER_DB[username] == hashed_attempt:
            clear_screen()
            role = ROLES[username]
            print(f"\n{Color.GREEN}✅ Authentication Successful.{Color.END}")
            print(f"Logged in as: {Color.BOLD}{username.upper()}{Color.END} [{role}]\n")
            return username, role
        else:
            attempts -= 1
            print(
                f"\n{Color.FAIL}❌ Invalid credentials. Attempts remaining: {attempts}{Color.END}\n"
            )

    print(
        f"\n{Color.FAIL}SECURITY LOCKOUT: Too many failed attempts. Exiting.{Color.END}"
    )
    sys.exit(1)


if __name__ == "__main__":
    require_login()
