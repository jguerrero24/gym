from flask import Blueprint
from controllers.auth import (
    list_users, login, logout, me,
    create_user, update_user, delete_user,
    my_clients, week_plan_get, week_plan_set
)

auth_bp = Blueprint("auth", __name__)

auth_bp.get("/api/users")(list_users)
auth_bp.post("/api/auth/login")(login)
auth_bp.post("/api/auth/logout")(logout)
auth_bp.get("/api/auth/me")(me)
auth_bp.post("/api/users")(create_user)
auth_bp.put("/api/users/<uid>")(update_user)
auth_bp.delete("/api/users/<uid>")(delete_user)
auth_bp.get("/api/my_clients")(my_clients)
auth_bp.get("/api/week_plan")(week_plan_get)
auth_bp.put("/api/week_plan/<int:dow>")(week_plan_set)
