import sqlite3

def get_user_vulnerable(username):
    conn = sqlite3.connect(':memory:')
    cursor = conn.cursor()
    # VULNERABLE: String concatenation
    query = f"SELECT * FROM users WHERE username = '{username}'"
    cursor.execute(query)
    result = cursor.fetchone()
    conn.close()
    return result