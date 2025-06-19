# VULNERABLE
from flask import redirect, request
def redirect_vulnerable():
    url = request.args.get('url')
    return redirect(url)