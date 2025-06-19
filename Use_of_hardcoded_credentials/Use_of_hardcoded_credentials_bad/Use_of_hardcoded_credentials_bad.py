# VULNERABLE
def api_request_vulnerable():
    api_key = "sk-1234567890abcdef"
    headers = {"Authorization": f"Bearer {api_key}"}
    return requests.get("https://api.example.com/data", headers=headers)
