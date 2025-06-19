from flask import Flask
app = Flask(__name__)

class CustomErrorHandler:
    def __init__(self, app):
        self.app = app
    
    def handle_error(self, error):
        # Log the error for debugging purposes
        self.app.logger.error(f"Internal Server Error: {str(error)}")
        
        # Return a generic error message to the user
        return "Internal Server Error", 500

@app.errorhandler(500)
def handle_error_secure(error):
    error_handler = CustomErrorHandler(app)
    return error_handler.handle_error(error)