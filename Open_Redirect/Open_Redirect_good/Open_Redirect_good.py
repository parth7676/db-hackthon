from flask import redirect, request, url_for
from urllib.parse import urlparse

def redirect_secure():
    try:
        # Get the URL from the request
        url = request.args.get('url')
        
        # Check if the URL is in the whitelist
        if url in get_whitelist_urls():
            return redirect(url)
        else:
            raise ValueError("Invalid URL")
    
    except Exception as e:
        print(f"Error: {e}")
        return redirect(url_for('index'))

def get_whitelist_urls():
    # Return a list of allowed URLs
    return ['https://example.com', 'https://www.example.com']