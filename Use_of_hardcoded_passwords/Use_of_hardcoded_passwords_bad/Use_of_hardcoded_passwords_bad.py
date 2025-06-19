def connect_db_vulnerable():
    # VULNERABLE: Hardcoded password
    password = "admin123"
    connection_string = f"postgresql://user:{password}@localhost/db"
    return connection_string