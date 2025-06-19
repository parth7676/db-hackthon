# VULNERABLE
import re
def validate_input_vulnerable(text):
    pattern = r'^(a+)+$'
    return re.match(pattern, text) is not None