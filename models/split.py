from config.db import get_db
import time

COLLECTION = "splits"

def _col():
    return get_db()[COLLECTION]

def serialize(doc):
    if doc is None:
        return None
    d = dict(doc)
    d["id"] = str(d.pop("_id"))
    return d

def find_for_user(uid):
    """Return splits with owner info (populated)."""
    db = get_db()
    pipeline = [
        {"$match": {"user_id": uid}},
        {"$lookup": {
            "from": "users",
            "localField": "owner_id",
            "foreignField": "_id",
            "as": "owner_doc"
        }},
        {"$addFields": {
            "owner_name":   {"$ifNull": [{"$first": "$owner_doc.name"},   None]},
            "owner_avatar": {"$ifNull": [{"$first": "$owner_doc.avatar"}, None]}
        }},
        {"$project": {"owner_doc": 0}}
    ]
    return [serialize(s) for s in db[COLLECTION].aggregate(pipeline)]

def upsert(data, actor_id):
    uid = data["user_id"]
    owner_id = actor_id if actor_id != uid else None
    doc = {
        "_id":      data["id"],
        "name":     data["name"],
        "type":     data["type"],
        "exercises": data["exercises"],
        "user_id":  uid,
        "owner_id": owner_id
    }
    _col().replace_one({"_id": data["id"]}, doc, upsert=True)

def delete(split_id):
    _col().delete_one({"_id": split_id})
    # Clear from week_plan
    get_db()["users"].update_many(
        {},
        [{"$set": {
            "week_plan": {
                "$arrayToObject": {
                    "$map": {
                        "input": {"$objectToArray": "$week_plan"},
                        "as":  "d",
                        "in": {
                            "k": "$$d.k",
                            "v": {"$cond": [{"$eq": ["$$d.v", split_id]}, None, "$$d.v"]}
                        }
                    }
                }
            }
        }}]
    )

def find_by_id(split_id):
    return serialize(_col().find_one({"_id": split_id}))

def assign_to_users(split_id, target_uids, actor_id):
    """Clone split into each target user's profile."""
    src = _col().find_one({"_id": split_id})
    if not src:
        return 0
    count = 0
    for tuid in target_uids:
        new_id = "s" + str(int(time.time() * 1000)) + tuid[-4:]
        _col().insert_one({
            "_id":       new_id,
            "name":      src["name"],
            "type":      src["type"],
            "exercises": src["exercises"],
            "user_id":   tuid,
            "owner_id":  actor_id
        })
        count += 1
        time.sleep(0.001)   # ensure unique timestamp ids
    return count
