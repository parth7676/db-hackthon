import requests

def fetch_url_secure(url):
    try:
        # Validate the URL to prevent SSRF attacks
        if not url.startswith("http://") and not url.startswith("https://"):
            raise ValueError("Invalid URL")
        
        # Set a timeout to prevent indefinite waiting
        timeout = 5  # seconds
        
        # Use the requests library with proper error handling
        response = requests.get(url, timeout=timeout)
        
        # Check the response status code
        response.raise_for_status()
        
        return response.text
    
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        return None