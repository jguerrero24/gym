from flask import session, request, jsonify
from models import user as UserModel

def get_current_user():
    uid = session.get("user_id")
    if not uid:
        return None
    return UserModel.find_by_id(uid)

def resolve_uid(requested_uid=None):
    """Return (effective_uid, actor) respecting role permissions."""
    actor = get_current_user()
    if not actor:
        return None, None
    if requested_uid and requested_uid != actor["id"]:
        if actor["role"] == "admin":
            return requested_uid, actor
        if actor["role"] == "profesor":
            from config.db import get_db
            t = get_db()["users"].find_one({
                "_id": requested_uid,
                "created_by": actor["id"],
                "active": True
            })
            if t:
                return requested_uid, actor
        return actor["id"], actor
    return actor["id"], actor

# ── Endpoints ─────────────────────────────────────────

def list_users():
    return jsonify(UserModel.find_all_active())

def login():
    d = request.json or {}
    uid  = d.get("user_id")
    pin  = str(d.get("pin", "")).strip()
    u = UserModel.find_by_id(uid)
    if not u:
        return jsonify({"error": "Usuario no encontrado"}), 404
    stored = u.get("pin") or ""
    if stored and stored != pin:
        return jsonify({"error": "PIN incorrecto"}), 403
    session["user_id"] = uid
    return jsonify({"ok": True, "user": {
        "id":     u["id"],
        "name":   u["name"],
        "role":   u["role"],
        "color":  u["color"],
        "avatar": u["avatar"]
    }})

def logout():
    session.clear()
    return jsonify({"ok": True})

def me():
    u = get_current_user()
    if not u:
        return jsonify({"error": "no_auth"}), 401
    return jsonify({"id": u["id"], "name": u["name"], "role": u["role"],
                    "color": u["color"], "avatar": u["avatar"]})

def create_user():
    actor = get_current_user()
    if not actor or actor["role"] not in ("admin", "profesor"):
        return jsonify({"error": "forbidden"}), 403
    d = request.json or {}
    role = d.get("role", "cliente")
    if actor["role"] == "profesor" and role != "cliente":
        return jsonify({"error": "forbidden"}), 403
    uid = UserModel.create(d, actor["id"])
    return jsonify({"ok": True, "id": uid})

def update_user(uid):
    actor = get_current_user()
    if not actor:
        return jsonify({"error": "no_auth"}), 401
    target = UserModel.find_by_id(uid)
    if not target:
        return jsonify({"error": "not found"}), 404
    if actor["role"] == "cliente" and actor["id"] != uid:
        return jsonify({"error": "forbidden"}), 403
    if actor["role"] == "profesor" and target.get("created_by") != actor["id"] and actor["id"] != uid:
        return jsonify({"error": "forbidden"}), 403
    UserModel.update(uid, request.json or {}, actor["role"])
    return jsonify({"ok": True})

def delete_user(uid):
    actor = get_current_user()
    if not actor or actor["role"] != "admin":
        return jsonify({"error": "forbidden"}), 403
    if uid == actor["id"]:
        return jsonify({"error": "No puedes eliminarte"}), 400
    UserModel.deactivate(uid)
    return jsonify({"ok": True})

def my_clients():
    actor = get_current_user()
    if not actor:
        return jsonify({"error": "no_auth"}), 401
    clients = UserModel.find_clients_of(actor)
    return jsonify([{
        "id":     str(c["_id"]),
        "name":   c["name"],
        "role":   c["role"],
        "color":  c.get("color", "#c8f25e"),
        "avatar": c.get("avatar", "👤")
    } for c in clients])

def week_plan_get():
    uid, _ = resolve_uid(request.args.get("user_id"))
    if not uid:
        return jsonify({"error": "no_auth"}), 401
    from config.db import get_db
    u = get_db()["users"].find_one({"_id": uid})
    plan = u.get("week_plan", {str(i): None for i in range(7)}) if u else {}
    return jsonify(plan)

def week_plan_set(dow):
    d = request.json or {}
    uid, _ = resolve_uid(d.get("user_id"))
    if not uid:
        return jsonify({"error": "no_auth"}), 401
    val = d.get("split_id")
    from config.db import get_db
    get_db()["users"].update_one(
        {"_id": uid},
        {"$set": {f"week_plan.{dow}": val}}
    )
    return jsonify({"ok": True})
