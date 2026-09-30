from datetime import date
from functools import wraps

from flask import Blueprint, abort, flash, g, redirect, render_template, request, url_for

from ..db import get_db
from ..auth.service import validate_csrf


main_bp = Blueprint("main", __name__)
VALID_PRIORITIES = {"low", "medium", "high"}
VALID_STATUSES = {"pending", "in_progress", "done"}


def login_required(view):
    @wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for("auth.login"))
        return view(**kwargs)

    return wrapped_view


def require_csrf():
    if not validate_csrf():
        abort(400, description="Token CSRF inválido.")


def get_owned_task(task_id):
    task = get_db().execute(
        "SELECT * FROM tasks WHERE id = ? AND user_id = ?", (task_id, g.user["id"])
    ).fetchone()
    if task is None:
        abort(404)
    return task


def validate_task_form():
    title = request.form.get("title", "").strip()
    description = request.form.get("description", "").strip()
    priority = request.form.get("priority", "medium")
    status = request.form.get("status", "pending")
    due_date = request.form.get("due_date", "").strip() or None

    if not title or len(title) > 120:
        return None, "O título é obrigatório e deve ter até 120 caracteres."
    if len(description) > 2000:
        return None, "A descrição deve ter até 2.000 caracteres."
    if priority not in VALID_PRIORITIES or status not in VALID_STATUSES:
        return None, "Prioridade ou status inválido."
    if due_date:
        try:
            date.fromisoformat(due_date)
        except ValueError:
            return None, "Informe um prazo válido."
    return (title, description, priority, status, due_date), None


@main_bp.route("/")
def index():
    if g.user:
        return redirect(url_for("main.dashboard"))
    return render_template("landing.html")


@main_bp.route("/dashboard")
@login_required
def dashboard():
    status_filter = request.args.get("status", "all")
    params = [g.user["id"]]
    query = "SELECT * FROM tasks WHERE user_id = ?"
    if status_filter in VALID_STATUSES:
        query += " AND status = ?"
        params.append(status_filter)
    else:
        status_filter = "all"
    query += " ORDER BY CASE priority WHEN 'high' THEN 1 WHEN 'medium' THEN 2 ELSE 3 END, due_date IS NULL, due_date, created_at DESC"
    tasks = get_db().execute(query, params).fetchall()
    return render_template("dashboard.html", tasks=tasks, status_filter=status_filter)


@main_bp.post("/tasks")
@login_required
def create_task():
    require_csrf()
    values, error = validate_task_form()
    if error:
        flash(error, "error")
        return redirect(url_for("main.dashboard"))

    db = get_db()
    db.execute(
        """
        INSERT INTO tasks (user_id, title, description, priority, status, due_date)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (g.user["id"], *values),
    )
    db.commit()
    flash("Tarefa criada.", "success")
    return redirect(url_for("main.dashboard"))


@main_bp.post("/tasks/<int:task_id>/update")
@login_required
def update_task(task_id):
    require_csrf()
    get_owned_task(task_id)
    values, error = validate_task_form()
    if error:
        flash(error, "error")
        return redirect(url_for("main.dashboard"))

    db = get_db()
    db.execute(
        """
        UPDATE tasks
        SET title = ?, description = ?, priority = ?, status = ?, due_date = ?,
            updated_at = CURRENT_TIMESTAMP
        WHERE id = ? AND user_id = ?
        """,
        (*values, task_id, g.user["id"]),
    )
    db.commit()
    flash("Tarefa atualizada.", "success")
    return redirect(url_for("main.dashboard"))


@main_bp.post("/tasks/<int:task_id>/toggle")
@login_required
def toggle_task(task_id):
    require_csrf()
    task = get_owned_task(task_id)
    next_status = "done" if task["status"] != "done" else "pending"
    db = get_db()
    db.execute(
        "UPDATE tasks SET status = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ? AND user_id = ?",
        (next_status, task_id, g.user["id"]),
    )
    db.commit()
    return redirect(url_for("main.dashboard"))


@main_bp.post("/tasks/<int:task_id>/delete")
@login_required
def delete_task(task_id):
    require_csrf()
    get_owned_task(task_id)
    db = get_db()
    db.execute("DELETE FROM tasks WHERE id = ? AND user_id = ?", (task_id, g.user["id"]))
    db.commit()
    flash("Tarefa removida.", "success")
    return redirect(url_for("main.dashboard"))
