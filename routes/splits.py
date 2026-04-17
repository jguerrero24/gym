from flask import Blueprint
from controllers.splits import (
    get_splits, save_split, delete_split,
    assign_split, assignable_clients
)

splits_bp = Blueprint("splits", __name__)

splits_bp.get("/api/splits")(get_splits)
splits_bp.post("/api/splits")(save_split)
splits_bp.delete("/api/splits/<split_id>")(delete_split)
splits_bp.post("/api/splits/<split_id>/assign")(assign_split)
splits_bp.get("/api/assignable_clients")(assignable_clients)
