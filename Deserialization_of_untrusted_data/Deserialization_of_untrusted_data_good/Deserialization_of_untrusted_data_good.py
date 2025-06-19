import pickle
import hmac
import hashlib

def load_data_secure(serialized_data, signature, secret_key):
    expected_signature = hmac.new(secret_key, serialized_data, hashlib.sha256).digest()
    if not hmac.compare_digest(expected_signature, signature):
        raise ValueError("Invalid signature")

    try:
        data = pickle.loads(serialized_data)
        return data
    except pickle.UnpicklingError as e:
        print(f"Error unpickling data: {e}")
        return None