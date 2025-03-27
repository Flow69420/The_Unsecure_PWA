import sqlite3 as sql
import time
import random
import html
import re

def is_password_complex(password):
    """
    Check if the password meets complexity requirements:
    - At least 8 characters long
    - Contains at least one uppercase letter
    - Contains at least one lowercase letter
    - Contains at least one digit
    - Contains at least one special character
    """
    if len(password) < 8:
        return False
    if not re.search(r"[A-Z]", password):
        return False
    if not re.search(r"[a-z]", password):
        return False
    if not re.search(r"[0-9]", password):
        return False
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        return False
    return True

def insertUser(username, password, DoB):
    # Enforce password complexity
    if not is_password_complex(password):
        raise ValueError("Password does not meet complexity requirements. It must be at least 8 characters long and include uppercase, lowercase, digit, and special character.")
    
    con = sql.connect("database_files/database.db")
    cur = con.cursor()
    try:
        # Check if username exists first (optional but improves UX)
        cur.execute("SELECT username FROM users WHERE username=?", (username,))
        if cur.fetchone():
            raise ValueError("Username already exists.")
        
        # Insert user (UNIQUE constraint will block duplicates)
        cur.execute(
            "INSERT INTO users (username, password, dateOfBirth) VALUES (?,?,?)",
            (username, password, DoB),
        )
        con.commit()
    except sql.IntegrityError as e:
        # Handle UNIQUE constraint violation (race condition)
        con.rollback()
        raise ValueError("Username already exists.") from e
    finally:
        con.close()


def retrieveUsers(username, password):
    con = sql.connect("database_files/database.db")
    cur = con.cursor()
    # Use a single parameterized query to check both username and password
    cur.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
    result = cur.fetchone()
    if result is None:
        con.close()
        return False
    else:
        # Plain text log of visitor count as requested by Unsecure PWA management
        with open("visitor_log.txt", "r") as file:
            number = int(file.read().strip())
            number += 1
        with open("visitor_log.txt", "w") as file:
            file.write(str(number))
        # Simulate response time of heavy app for testing purposes
        time.sleep(random.randint(80, 90) / 1000)
        con.close()
        return True


def insertFeedback(feedback):
    con = sql.connect("database_files/database.db")
    cur = con.cursor()
    # Use parameterized query to insert feedback
    cur.execute("INSERT INTO feedback (feedback) VALUES (?)", (feedback,))
    con.commit()
    con.close()


def listFeedback():
    con = sql.connect("database_files/database.db")
    cur = con.cursor()
    data = cur.execute("SELECT * FROM feedback").fetchall()
    con.close()
    # Write output to HTML with proper escaping to prevent XSS
    with open("templates/partials/success_feedback.html", "w") as f:
        for row in data:
            f.write("<p>\n")
            # Escape any special HTML characters in the feedback before writing it out
            f.write(html.escape(row[1]))
            f.write("\n</p>\n")
