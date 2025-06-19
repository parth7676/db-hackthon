import sqlite3

def get_user_secure(username):
    # Create a connection to the database
    conn = sqlite3.connect(':memory:')
    cursor = conn.cursor()
    
    # Use parameterized query to prevent SQL injection
    query = "SELECT * FROM users WHERE username =?"
    cursor.execute(query, (username,))
    
    # Fetch the result
    result = cursor.fetchone()
    
    # Close the connection
    conn.close()
    
    return result