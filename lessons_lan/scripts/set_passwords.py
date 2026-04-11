"""
Project: Homeschool Lessons (Dream.OS)
File: scripts/set_passwords.py
Purpose: One-off local script to set student passwords in the SQLite DB.
Owner: Local family deployment (homeschool)
"""

import os
import sqlite3

from werkzeug.security import generate_password_hash


def main():
    db_path = os.path.join(os.path.dirname(__file__), "..", "instance", "homeschool.db")
    db_path = os.path.abspath(db_path)

    con = sqlite3.connect(db_path)
    cur = con.cursor()
    cur.execute(
        "UPDATE users SET password_hash=? WHERE username=?",
        (generate_password_hash("34086028"), "charlie"),
    )
    cur.execute(
        "UPDATE users SET password_hash=? WHERE username=?",
        (generate_password_hash("0822"), "chris"),
    )
    con.commit()
    con.close()
    print("updated")


if __name__ == "__main__":
    main()

