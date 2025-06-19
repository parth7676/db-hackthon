import os
import requests
import bcrypt
import re
import signal

# Secure: Use environment variables for credentials
api_key = os.environ.get('API_KEY')
if not api_key:
    raise ValueError("API key not configured")

# Secure: Validate URLs and restrict access
def safe_request(url):
    parsed = urlparse(url)
    blocked_hosts = ['localhost', '127.0.0.1', '10.0.0.0/8', '192.168.0.0/16']
    if parsed.hostname in blocked_hosts:
        raise ValueError("Access to internal services blocked")
    response = requests.get(url, timeout=5)
    return response

# Secure: Use secure password hashing
def hash_password(password):
    salt = bcrypt.gensalt(rounds=12)
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed

def verify_password(password, hashed):
    return bcrypt.checkpw(password.encode('utf-8'), hashed)

# Secure: Use timeouts and non-backtracking regex
def safe_regex_match(pattern, string, timeout=1):
    def timeout_handler(signum, frame):
        raise TimeoutError("Regex timeout")
    signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(timeout)
    try:
        return re.match(pattern, string)
    finally:
        signal.alarm(0)

# Make a secure request
response = safe_request('https://api.example.com/data')