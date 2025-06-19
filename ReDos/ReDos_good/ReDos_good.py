import re
import signal

def validate_input_secure(text):
    try:
        # Set a timeout to prevent ReDoS attacks
        signal.alarm(1)
        
        # Use a possession-free regular expression
        pattern = r'^a+$'
        return re.match(pattern, text) is not None
    
    except re.error as e:
        print(f"Error: {e}")
        return False
    except TimeoutError:
        print("Timeout: ReDoS attack detected")
        return False
    finally:
        signal.alarm(0)