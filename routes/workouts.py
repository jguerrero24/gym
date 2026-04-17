from flask import Blueprint
from controllers.workouts import get_workouts, save_workout, delete_workout

workouts_bp = Blueprint("workouts", __name__)

workouts_bp.get("/api/workouts")(get_workouts)
workouts_bp.post("/api/workouts")(save_workout)
workouts_bp.delete("/api/workouts/<workout_id>")(delete_workout)
