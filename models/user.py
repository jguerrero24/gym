from config.db import get_db
from bson import ObjectId
import time

COLLECTION = "users"

def _col():
    return get_db()[COLLECTION]

def serialize(doc):
    if doc is None:
        return None
    d = dict(doc)
    d["id"] = str(d.pop("_id"))
    d.pop("pin", None)           # never expose pin in responses
    d["has_pin"] = bool(doc.get("pin"))
    return d

def serialize_full(doc):
    """Include pin — only used internally."""
    if doc is None:
        return None
    d = dict(doc)
    d["id"] = str(d.pop("_id"))
    return d

# ── Seed ──────────────────────────────────────────────
DEFAULT_EXERCISES = [
    ("Press banca plano","Pectoral"),("Press banca inclinado","Pectoral"),
    ("Press banca declinado","Pectoral"),("Aperturas con mancuernas","Pectoral"),
    ("Fondos en paralelas","Pectoral"),("Crossover cable","Pectoral"),
    ("Press militar barra","Hombros"),("Press Arnold","Hombros"),
    ("Elevaciones laterales","Hombros"),("Elevaciones frontales","Hombros"),
    ("Face pull","Hombros"),("Pájaros","Hombros"),
    ("Press francés","Tríceps"),("Extensión tríceps polea","Tríceps"),
    ("Fondos tríceps","Tríceps"),("Patada de tríceps","Tríceps"),
    ("Press cerrado banca","Tríceps"),
    ("Dominadas","Dorsal"),("Jalón al pecho","Dorsal"),
    ("Remo con barra","Dorsal"),("Remo con mancuerna","Dorsal"),
    ("Remo en polea baja","Dorsal"),("Pull-over","Dorsal"),
    ("Curl bíceps barra","Bíceps"),("Curl bíceps mancuernas","Bíceps"),
    ("Curl martillo","Bíceps"),("Curl predicador","Bíceps"),("Curl concentrado","Bíceps"),
    ("Encogimientos","Trapecio"),("Remo al mentón","Trapecio"),
    ("Sentadilla","Cuádriceps"),("Prensa","Cuádriceps"),
    ("Extensión cuádriceps","Cuádriceps"),("Sentadilla búlgara","Cuádriceps"),
    ("Zancadas","Cuádriceps"),("Hack squat","Cuádriceps"),
    ("Peso muerto","Isquiotibiales"),("Curl femoral","Isquiotibiales"),
    ("Peso muerto rumano","Isquiotibiales"),("Buenos días","Isquiotibiales"),
    ("Hip thrust","Glúteos"),("Patada de glúteo","Glúteos"),
    ("Sentadilla sumo","Glúteos"),("Step-up","Glúteos"),("Abducción cadera","Glúteos"),
    ("Elevación de gemelos de pie","Pantorrillas"),
    ("Elevación de gemelos sentado","Pantorrillas"),
    ("Crunch","Abdomen"),("Plancha","Abdomen"),("Rueda abdominal","Abdomen"),
    ("Crunch inverso","Abdomen"),("Elevación de piernas","Abdomen"),
    ("Russian twist","Abdomen"),
]

def seed():
    db = get_db()
    # Seed admin user
    if db[COLLECTION].count_documents({"active": True}) == 0:
        db[COLLECTION].insert_one({
            "_id": "u_admin",
            "name": "Admin",
            "role": "admin",
            "pin": "0000",
            "color": "#c8f25e",
            "avatar": "👑",
            "created_by": None,
            "active": True,
            "week_plan": {str(i): None for i in range(7)}
        })

    # Seed global exercises
    if db["exercises"].count_documents({"user_id": None}) == 0:
        db["exercises"].insert_many([
            {"name": n, "muscle_group": mg, "custom": False, "user_id": None}
            for n, mg in DEFAULT_EXERCISES
        ])

# ── CRUD ─────────────────────────────────────────────
def find_all_active():
    return [serialize(u) for u in _col().find({"active": True}).sort([("role", 1), ("name", 1)])]

def find_by_id(uid):
    return serialize_full(_col().find_one({"_id": uid, "active": True}))

def create(data, creator_id):
    uid = "u_" + str(int(time.time() * 1000))
    doc = {
        "_id": uid,
        "name": data["name"].strip(),
        "role": data.get("role", "cliente"),
        "pin": str(data.get("pin", "")).strip() or None,
        "color": data.get("color", "#7c6dfa"),
        "avatar": data.get("avatar", "👤"),
        "created_by": creator_id,
        "active": True,
        "week_plan": {str(i): None for i in range(7)}
    }
    _col().insert_one(doc)
    return uid

def update(uid, data, actor_role):
    fields = {}
    for k in ("name", "color", "avatar"):
        if k in data:
            fields[k] = str(data[k]).strip()
    if "pin" in data:
        fields["pin"] = str(data["pin"]).strip() or None
    if actor_role == "admin" and "role" in data:
        fields["role"] = data["role"]
    if fields:
        _col().update_one({"_id": uid}, {"$set": fields})

def deactivate(uid):
    _col().update_one({"_id": uid}, {"$set": {"active": False}})

def find_clients_of(actor):
    if actor["role"] == "admin":
        return list(_col().find({"active": True, "_id": {"$ne": actor["id"]}},
                                {"pin": 0}).sort("name", 1))
    elif actor["role"] == "profesor":
        return list(_col().find({"active": True, "created_by": actor["id"]},
                                {"pin": 0}).sort("name", 1))
    return []
