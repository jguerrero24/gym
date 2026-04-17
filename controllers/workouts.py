from flask import request, jsonify
from controllers.auth import get_current_user, resolve_uid
from models import workout as WorkoutModel

def get_workouts():
    uid, _ = resolve_uid(request.args.get("user_id"))
    if not uid:
        return jsonify({"error": "no_auth"}), 401
    docs = WorkoutModel.find_for_user(uid)
    return jsonify([{
        "id":        d["id"],
        "date":      d.get("date"),
        "dow":       d.get("dow"),
        "splitId":   d.get("split_id"),
        "splitName": d.get("split_name"),
        "splitType": d.get("split_type"),
        "startTime": d.get("start_time"),
        "exercises": d.get("exercises", [])
    } for d in docs])

def save_workout():
    actor = get_current_user()
    if not actor:
        return jsonify({"error": "no_auth"}), 401
    d = request.json or {}
    uid, _ = resolve_uid(d.get("user_id"))
    WorkoutModel.upsert(d, uid)
    return jsonify({"ok": True})

def delete_workout(workout_id):
    actor = get_current_user()
    if not actor:
        return jsonify({"error": "no_auth"}), 401
    uid, _ = resolve_uid()
    WorkoutModel.delete(workout_id, uid)
    return jsonify({"ok": True})
