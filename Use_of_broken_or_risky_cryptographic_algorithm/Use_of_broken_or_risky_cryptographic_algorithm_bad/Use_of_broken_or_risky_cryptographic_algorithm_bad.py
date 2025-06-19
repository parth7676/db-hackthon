# VULNERABLE
import hashlib
def hash_data_vulnerable(data):
    return hashlib.md5(data.encode()).hexdigest()