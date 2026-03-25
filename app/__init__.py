import os
from flask import Flask
from .db import init_db


def create_app() -> Flask:
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY=os.getenv("SECRET_KEY", "dev-secret-key"),
        DATABASE=os.getenv("DATABASE_PATH", os.path.join(app.instance_path, "materials.db")),
    )

    os.makedirs(app.instance_path, exist_ok=True)
    db_dir = os.path.dirname(app.config["DATABASE"])
    if db_dir:
        os.makedirs(db_dir, exist_ok=True)

    init_db(app)

    from .routes import bp
    app.register_blueprint(bp)

    return app
