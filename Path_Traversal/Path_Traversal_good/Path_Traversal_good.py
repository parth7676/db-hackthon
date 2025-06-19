import os

def read_file_secure(filename):
    # Define the base directory for uploads
    base_dir = "/var/uploads/"
    
    # Validate the filename to prevent directory traversal attacks
    if ".." in filename or "/" in filename or "\\" in filename:
        raise ValueError("Invalid filename")
    
    # Construct the file path using os.path.join to prevent path manipulation
    file_path = os.path.join(base_dir, filename)
    
    # Check if the file exists and is a regular file
    if not os.path.isfile(file_path):
        raise FileNotFoundError("File not found")
    
    # Read the file
    try:
        with open(file_path, 'r') as f:
            return f.read()
    except Exception as e:
        print(f"Error reading file: {e}")
        return None