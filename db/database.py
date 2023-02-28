from pymongo import MongoClient
from config import MONGODB_URL
import certifi

def get_database():
    
    client = MongoClient(MONGODB_URL, serverSelectionTimeoutMS=5000, tlsCAFile=certifi.where())
    
    try:
        print(client['test'])
    except Exception:
        print("Unable to connect to the server.")
        
    return client

client = get_database()
