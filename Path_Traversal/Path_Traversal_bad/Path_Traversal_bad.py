# VULNERABLE
def read_file_vulnerable(filename):
    file_path = "/var/uploads/" + filename
    with open(file_path, 'r') as f:
        return f.read()