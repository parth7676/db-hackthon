from argon2 import PasswordHasher

def hash_data_secure(data):
    try:
        # Create an Argon2 password hasher
        ph = PasswordHasher()
        
        # Hash the data using Argon2
        hashed_data = ph.hash(data)
        
        # Return the hashed data
        return hashed_data
    
    except Exception as e:
        # Handle any exceptions that occur during the hashing process
        print(f"Error hashing data: {e}")
        return None