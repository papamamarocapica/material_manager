import sqlite3
from pathlib import Path
from flask import current_app, g


SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS materials (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    url TEXT NOT NULL,
    course TEXT NOT NULL,
    tags TEXT DEFAULT '',
    memo TEXT DEFAULT '',
    favorite INTEGER NOT NULL DEFAULT 0,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TRIGGER IF NOT EXISTS trg_materials_updated_at
AFTER UPDATE ON materials
FOR EACH ROW
WHEN NEW.updated_at = OLD.updated_at
BEGIN
    UPDATE materials
       SET updated_at = CURRENT_TIMESTAMP
     WHERE id = NEW.id;
END;
"""


def get_db() -> sqlite3.Connection:
    if "db" not in g:
        g.db = sqlite3.connect(current_app.config["DATABASE"])
        g.db.row_factory = sqlite3.Row
    return g.db


def close_db(e=None) -> None:
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db(app) -> None:
    Path(app.config["DATABASE"]).parent.mkdir(parents=True, exist_ok=True)
    with app.app_context():
        db = get_db()
        db.executescript(SCHEMA_SQL)
        db.commit()
    app.teardown_appcontext(close_db)
