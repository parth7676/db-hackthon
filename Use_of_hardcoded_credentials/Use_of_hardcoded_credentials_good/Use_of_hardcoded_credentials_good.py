import requests
import os

def api_request_secure():
    try:
        # Load the API key from an environment variable
        api_key = os.environ.get("API_KEY")
        
        # Check if the API key is set
        if not api_key:
            raise ValueError("API key is not set")
        
        # Set the headers with the API key
        headers = {"Authorization": f"Bearer {api_key}"}
        
        # Set the timeout to prevent indefinite waiting
        timeout = 5  # seconds
        
        # Make the request with proper error handling
        response = requests.get("https://api.example.com/data", headers=headers, timeout=timeout)
        
        # Check the response status code
        response.raise_for_status()
        
        return response.text
    
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        return None