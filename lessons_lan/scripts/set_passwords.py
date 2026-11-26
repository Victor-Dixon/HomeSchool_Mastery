"""Operator-only local student password rotation. Never invoked by app startup."""
import getpass
import os
import sqlite3

from werkzeug.security import generate_password_hash


def main():
    db_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "instance", "homeschool.db"))
    if not os.path.isfile(db_path):
        raise SystemExit("Existing household database required.")
    passwords = {}
    for username in ("charlie", "chris"):
        password = getpass.getpass(f"New password for {username}: ")
        if len(password) < 16 or not password.strip() or password != getpass.getpass("Confirm password: "):
            raise SystemExit("Password must match and contain at least 16 characters.")
        passwords[username] = password
    if len(set(passwords.values())) != len(passwords):
        raise SystemExit("Choose distinct passwords.")
    if input("Rotate both existing student passwords? Type ROTATE: ") != "ROTATE":
        raise SystemExit("Cancelled.")
    con = sqlite3.connect(db_path)
    try:
        with con:
            for username, password in passwords.items():
                result = con.execute("UPDATE users SET password_hash=? WHERE username=? AND is_admin=0",
                                     (generate_password_hash(password), username))
                if result.rowcount != 1:
                    raise RuntimeError("Expected exactly one existing student; rolled back.")
    finally:
        con.close()
    print("Student passwords updated.")


if __name__ == "__main__":
    main()
