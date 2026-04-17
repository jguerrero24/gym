from flask import request, jsonify
from controllers.auth import get_current_user, resolve_uid
from models import split as SplitModel
from config.db import get_db

def get_splits():
    uid, _ = resolve_uid(request.args.get("user_id"))
    if not uid:
        return jsonify({"error": "no_auth"}), 401
    return jsonify(SplitModel.find_for_user(uid))

def save_split():
    actor = get_current_user()
    if not actor:
        return jsonify({"error": "no_auth"}), 401
    d = request.json or {}
    target_uid, _ = resolve_uid(d.get("user_id"))
    d["user_id"] = target_uid
    SplitModel.upsert(d, actor["id"])
    return jsonify({"ok": True})

def delete_split(split_id):
    actor = get_current_user()
    if not actor:
        return jsonify({"error": "no_auth"}), 401
    row = SplitModel.find_by_id(split_id)
    if not row:
        return jsonify({"error": "not found"}), 404
    if (actor["role"] != "admin"
            and row.get("user_id") != actor["id"]
            and row.get("owner_id") != actor["id"]):
        return jsonify({"error": "forbidden"}), 403
    SplitModel.delete(split_id)
    return jsonify({"ok": True})

def assign_split(split_id):
    actor = get_current_user()
    if not actor or actor["role"] not in ("admin", "profesor"):
        return jsonify({"error": "forbidden"}), 403
    d = request.json or {}
    target_uids = d.get("user_ids", [])
    # For profesor: filter to only their own clients
    if actor["role"] == "profesor":
        allowed = {str(u["_id"]) for u in get_db()["users"].find({
            "created_by": actor["id"], "active": True
        }, {"_id": 1})}
        target_uids = [u for u in target_uids if u in allowed]
    count = SplitModel.assign_to_users(split_id, target_uids, actor["id"])
    return jsonify({"ok": True, "assigned": count})

def assignable_clients():
    actor = get_current_user()
    if not actor:
        return jsonify({"error": "no_auth"}), 401
    if actor["role"] == "admin":
        docs = list(get_db()["users"].find(
            {"active": True, "_id": {"$ne": actor["id"]}},
            {"pin": 0}
        ).sort("name", 1))
    elif actor["role"] == "profesor":
        docs = list(get_db()["users"].find(
            {"active": True, "created_by": actor["id"]},
            {"pin": 0}
        ).sort("name", 1))
    else:
        docs = []
    return jsonify([{
        "id":     str(d["_id"]),
        "name":   d["name"],
        "role":   d.get("role", "cliente"),
        "color":  d.get("color", "#c8f25e"),
        "avatar": d.get("avatar", "👤")
    } for d in docs])
