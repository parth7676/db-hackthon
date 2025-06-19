import tempfile

def create_temp_file_secure():
    # Create a temporary file with a unique name
    with tempfile.NamedTemporaryFile(mode='w', delete=False) as temp_file:
        # Write sensitive data to the temporary file
        temp_file.write("sensitive data")
        # Return the name of the temporary file
        return temp_file.name