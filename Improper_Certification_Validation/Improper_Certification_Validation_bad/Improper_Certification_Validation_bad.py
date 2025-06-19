# VULNERABLE
import ssl
import urllib.request
def fetch_data_vulnerable(url):
    context = ssl.create_default_context()
    context.check_hostname = False
    context.verify_mode = ssl.CERT_NONE
    response = urllib.request.urlopen(url, context=context)
    return response.read()