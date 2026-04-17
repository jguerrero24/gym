import os
from pymongo import MongoClient

_client = None
_db     = None

ATLAS_URI = (
    "mongodb+srv://joard9194_db_user:ujicMmsD8QYLxYrP"
    "@cluster0.9qycdz3.mongodb.net/gymlog"
    "?retryWrites=true&w=majority&appName=Cluster0"
)

def get_db():
    global _client, _db
    if _db is not None:
        return _db
    uri    = os.environ.get("MONGODB_URI", ATLAS_URI)
    db_name = os.environ.get("MONGODB_DB", "gymlog")
    _client = MongoClient(uri, serverSelectionTimeoutMS=10000)
    _db     = _client[db_name]
    return _db
