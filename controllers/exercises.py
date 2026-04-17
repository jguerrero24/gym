from flask import request, jsonify
from controllers.auth import get_current_user, resolve_uid
from models import exercise as ExModel

def get_exercises():
    uid, _ = resolve_uid(request.args.get("user_id"))
    if not uid:
        return jsonify({"error": "no_auth"}), 401
    return jsonify(ExModel.find_for_user(uid))

def add_exercise():
    uid, _ = resolve_uid()
    if not uid:
        return jsonify({"error": "no_auth"}), 401
    d = request.json or {}
    ExModel.create(d.get("name", ""), d.get("muscle_group", ""), uid)
    return jsonify({"ok": True})

def update_exercise(ex_id):
    uid, _ = resolve_uid()
    if not uid:
        return jsonify({"error": "no_auth"}), 401
    d = request.json or {}
    # Get old name for cascade rename
    from config.db import get_db
    old = get_db()["exercises"].find_one({"_id": __import__("bson").ObjectId(ex_id)})
    if not old:
        return jsonify({"error": "not found"}), 404
    old_name = old["name"]
    new_name = d.get("name", old_name).strip()
    ExModel.update(ex_id, new_name, d.get("muscle_group", old["muscle_group"]))
    if old_name != new_name:
        ExModel.rename_in_splits_and_workouts(uid, old_name, new_name)
    return jsonify({"ok": True})

def delete_exercise(ex_id):
    actor = get_current_user()
    if not actor:
        return jsonify({"error": "no_auth"}), 401
    ExModel.delete(ex_id)
    return jsonify({"ok": True})
