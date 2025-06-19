import os
from cryptography.fernet import Fernet

def encrypt_data_secure(data):
    try:
        # Load the encryption key from an environment variable
        encryption_key = os.environ.get("ENCRYPTION_KEY")
        
        # Check if the encryption key is set
        if not encryption_key:
            raise ValueError("Encryption key is not set")
        
        # Create a Fernet object with the encryption key
        cipher = Fernet(encryption_key)
        
        # Convert the data to bytes
        data_bytes = data.encode("utf-8")
        
        # Encrypt the data
        encrypted_data = cipher.encrypt(data_bytes)
        
        return encrypted_data
    
    except Exception as e:
        print(f"Error: {e}")
        return None