# VULNERABLE
import tempfile
def create_temp_file_vulnerable():
    temp_file = open('/tmp/myapp_temp.txt', 'w')
    temp_file.write("sensitive data")
    return temp_file.name