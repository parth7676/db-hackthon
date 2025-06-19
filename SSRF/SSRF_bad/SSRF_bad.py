# VULNERABLE
import requests
def fetch_url_vulnerable(url):
    response = requests.get(url)
    return response.text

