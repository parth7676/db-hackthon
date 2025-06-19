# VULNERABLE
from flask import Flask
app = Flask(__name__)
@app.errorhandler(500)
def handle_error_vulnerable(error):
    return f"Internal Server Error: {str(error)}", 500