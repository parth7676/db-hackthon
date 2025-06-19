from flask import Flask
import os

app = Flask(__name__)

# Load configuration from environment variables
app.config['DEBUG'] = os.environ.get('DEBUG', 'False') == 'True'
app.config['HOST'] = os.environ.get('HOST', 'localhost')
app.config['PORT'] = int(os.environ.get('PORT', 5000))

if __name__ == '__main__':
    app.run(host=app.config['HOST'], port=app.config['PORT'])