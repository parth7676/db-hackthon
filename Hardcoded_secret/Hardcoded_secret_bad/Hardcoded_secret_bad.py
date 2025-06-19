# VULNERABLE
def encrypt_data_vulnerable(data):
    secret_key = "my_secret_encryption_key_123"
    encrypted = encrypt(data, secret_key)
    return encrypted