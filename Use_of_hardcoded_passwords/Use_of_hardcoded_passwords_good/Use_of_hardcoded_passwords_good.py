import os

def connect_db_secure():
    try:
        # Load the password from an environment variable
        password = os.environ.get("DB_PASSWORD")
        
        # Check if the password is set
        if not password:
            raise ValueError("Database password is not set")
        
        # Load the database connection details from environment variables
        username = os.environ.get("DB_USERNAME")
        host = os.environ.get("DB_HOST")
        database = os.environ.get("DB_NAME")
        
        # Check if the database connection details are set
        if not username or not host or not database:
            raise ValueError("Database connection details are not set")
        
        # Construct the connection string
        connection_string = f"postgresql://{username}:{password}@{host}/{database}"
        
        return connection_string
    
    except Exception as e:
        print(f"Error: {e}")
        return None