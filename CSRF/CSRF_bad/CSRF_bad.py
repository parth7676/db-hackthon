# VULNERABLE
from flask import Flask, request
app = Flask(__name__)
@app.route('/transfer', methods=['POST'])
def transfer_money_vulnerable():
    amount = request.form.get('amount')
    to_account = request.form.get('to_account')
    perform_transfer(amount, to_account)
    return "Transfer completed"