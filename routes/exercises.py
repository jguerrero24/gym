from flask import Blueprint
from controllers.exercises import (
    get_exercises, add_exercise, update_exercise, delete_exercise
)

exercises_bp = Blueprint("exercises", __name__)

exercises_bp.get("/api/exercises")(get_exercises)
exercises_bp.post("/api/exercises")(add_exercise)
exercises_bp.put("/api/exercises/<ex_id>")(update_exercise)
exercises_bp.delete("/api/exercises/<ex_id>")(delete_exercise)
