import sqlite3

from flask import current_app, g


class PostgresDatabase:
    def __init__(self, connection):
        self.connection = connection

    def execute(self, query, params=()):
        return self.connection.execute(query.replace("?", "%s"), params)

    def commit(self):
        self.connection.commit()

    def rollback(self):
        self.connection.rollback()

    def close(self):
        self.connection.close()


def get_db():
    if "db" not in g:
        database_url = current_app.config.get("DATABASE_URL")
        if database_url:
            import psycopg
            from psycopg.rows import dict_row

            connection = psycopg.connect(database_url, row_factory=dict_row)
            g.db = PostgresDatabase(connection)
        else:
            g.db = sqlite3.connect(current_app.config["DATABASE"])
            g.db.row_factory = sqlite3.Row
            g.db.execute("PRAGMA foreign_keys = ON")
    return g.db


def close_db(_error=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    db = get_db()
    if current_app.config.get("DATABASE_URL"):
        with current_app.open_resource("schema_postgres.sql") as schema_file:
            schema = schema_file.read().decode("utf-8")
        for statement in schema.split(";"):
            if statement.strip():
                db.execute(statement)
    else:
        with current_app.open_resource("schema.sql") as schema_file:
            schema = schema_file.read().decode("utf-8")
        db.executescript(schema)
    db.commit()
