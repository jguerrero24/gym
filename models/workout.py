from config.db import get_db

COLLECTION = "workouts"

def _col():
    return get_db()[COLLECTION]

def serialize(doc):
    if doc is None:
        return None
    d = dict(doc)
    d["id"] = str(d.pop("_id"))
    return d

def find_for_user(uid):
    docs = list(_col().find({"user_id": uid}).sort([("date", -1), ("start_time", -1)]))
    return [serialize(d) for d in docs]

def upsert(data, uid):
    doc = {
        "_id":        data["id"],
        "user_id":    uid,
        "date":       data["date"],
        "dow":        data["dow"],
        "split_id":   data.get("splitId"),
        "split_name": data.get("splitName"),
        "split_type": data.get("splitType"),
        "start_time": data.get("startTime"),
        "exercises":  data["exercises"]
    }
    _col().replace_one({"_id": data["id"]}, doc, upsert=True)
    return serialize(doc)

def delete(workout_id, uid):
    _col().delete_one({"_id": workout_id, "user_id": uid})
