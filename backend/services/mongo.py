import os
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")

# In-memory fallback when MongoDB is not available
class InMemoryCollection:
    def __init__(self):
        self._data = {}

    def find_one(self, query):
        key = query.get("sessionId")
        return self._data.get(key)

    def update_one(self, query, update, upsert=False):
        key = query.get("sessionId")
        doc = self._data.get(key, {})
        if "$set" in update:
            doc.update(update["$set"])
        if "$setOnInsert" in update and key not in self._data:
            doc.update(update["$setOnInsert"])
        if upsert or key in self._data:
            doc["sessionId"] = key
            self._data[key] = doc

class InMemoryDB:
    def __init__(self):
        self.applications = InMemoryCollection()
        self.documents = InMemoryCollection()
        self.decisions = InMemoryCollection()
        self.sanctions = InMemoryCollection()

# Try MongoDB, fall back to in-memory
try:
    from pymongo import MongoClient
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=2000)
    client.admin.command('ping')
    db = client.ai_loan_advisor
    print("Connected to MongoDB")
except Exception as e:
    print(f"MongoDB not available ({e}), using in-memory storage")
    db = InMemoryDB()
