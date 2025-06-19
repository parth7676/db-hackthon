# VULNERABLE
import pickle
def load_data_vulnerable(serialized_data):
    data = pickle.loads(serialized_data)
    return data

