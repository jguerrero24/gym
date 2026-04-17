from .auth      import auth_bp
from .exercises import exercises_bp
from .splits    import splits_bp
from .workouts  import workouts_bp

def register_routes(app):
    app.register_blueprint(auth_bp)
    app.register_blueprint(exercises_bp)
    app.register_blueprint(splits_bp)
    app.register_blueprint(workouts_bp)
