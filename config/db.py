import os
from pymongo import MongoClient

_client = None
_db     = None

def get_db():
    global _client, _db
    if _db is not None:
        return _db
    uri = os.environ.get("MONGODB_URI")
    if not uri:
        raise RuntimeError(
            "MONGODB_URI no está configurada. "
            "Crea un archivo .env con MONGODB_URI=tu_connection_string"
        )
    db_name = os.environ.get("MONGODB_DB", "gymlog")
    _client = MongoClient(uri, serverSelectionTimeoutMS=10000)
    _db     = _client[db_name]
    return _db
