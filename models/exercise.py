from config.db import get_db
from bson import ObjectId

COLLECTION = "exercises"

def _col():
    return get_db()[COLLECTION]

def serialize(doc):
    d = dict(doc)
    d["id"] = str(d.pop("_id"))
    return d

def find_for_user(uid):
    """Return global exercises + user-specific ones, grouped by muscle_group."""
    docs = list(_col().find({"$or": [{"user_id": None}, {"user_id": uid}]})
                .sort([("muscle_group", 1), ("name", 1)]))
    grouped = {}
    for doc in docs:
        mg = doc["muscle_group"]
        grouped.setdefault(mg, []).append({
            "id": str(doc["_id"]),
            "name": doc["name"],
            "muscle_group": mg,
            "custom": doc.get("custom", False)
        })
    return grouped

def create(name, muscle_group, uid):
    result = _col().insert_one({
        "name": name.strip(),
        "muscle_group": muscle_group.strip(),
        "custom": True,
        "user_id": uid
    })
    return str(result.inserted_id)

def update(ex_id, name, muscle_group):
    _col().update_one(
        {"_id": ObjectId(ex_id)},
        {"$set": {"name": name.strip(), "muscle_group": muscle_group.strip()}}
    )

def delete(ex_id):
    _col().delete_one({"_id": ObjectId(ex_id)})

def rename_in_splits_and_workouts(uid, old_name, new_name):
    """Cascade rename across splits and workouts for a user."""
    db = get_db()
    # Splits
    for s in db["splits"].find({"user_id": uid}):
        exs = s.get("exercises", [])
        if any(e["name"] == old_name for e in exs):
            for e in exs:
                if e["name"] == old_name:
                    e["name"] = new_name
            db["splits"].update_one({"_id": s["_id"]}, {"$set": {"exercises": exs}})
    # Workouts
    for w in db["workouts"].find({"user_id": uid}):
        exs = w.get("exercises", [])
        if any(e["name"] == old_name for e in exs):
            for e in exs:
                if e["name"] == old_name:
                    e["name"] = new_name
            db["workouts"].update_one({"_id": w["_id"]}, {"$set": {"exercises": exs}})
