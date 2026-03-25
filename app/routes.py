from urllib.parse import urlparse
from flask import (
    Blueprint,
    flash,
    redirect,
    render_template,
    request,
    url_for,
)
from .db import get_db

bp = Blueprint("materials", __name__)


def _normalize_tags(raw_tags: str) -> str:
    items = [tag.strip() for tag in raw_tags.split(",") if tag.strip()]
    seen = []
    for tag in items:
        if tag not in seen:
            seen.append(tag)
    return ", ".join(seen)


def _validate_form(form):
    title = form.get("title", "").strip()
    url = form.get("url", "").strip()
    course = form.get("course", "").strip()
    tags = _normalize_tags(form.get("tags", ""))
    memo = form.get("memo", "").strip()
    favorite = 1 if form.get("favorite") == "on" else 0

    errors = []
    if not title:
        errors.append("タイトルは必須です。")
    if not url:
        errors.append("URLは必須です。")
    else:
        parsed = urlparse(url)
        if parsed.scheme not in {"http", "https"} or not parsed.netloc:
            errors.append("URLは http または https で入力してください。")
    if not course:
        errors.append("科目名は必須です。")

    return {
        "title": title,
        "url": url,
        "course": course,
        "tags": tags,
        "memo": memo,
        "favorite": favorite,
    }, errors


@bp.route("/")
def index():
    q = request.args.get("q", "").strip()
    course = request.args.get("course", "").strip()
    favorites_only = request.args.get("favorite", "") == "1"

    db = get_db()

    filters = []
    params = []

    if q:
        filters.append("(title LIKE ? OR url LIKE ? OR course LIKE ? OR tags LIKE ? OR memo LIKE ?)")
        keyword = f"%{q}%"
        params.extend([keyword, keyword, keyword, keyword, keyword])

    if course:
        filters.append("course = ?")
        params.append(course)

    if favorites_only:
        filters.append("favorite = 1")

    where_clause = f"WHERE {' AND '.join(filters)}" if filters else ""

    materials = db.execute(
        f"""
        SELECT id, title, url, course, tags, memo, favorite, created_at, updated_at
          FROM materials
          {where_clause}
         ORDER BY favorite DESC, updated_at DESC, id DESC
        """,
        params,
    ).fetchall()

    courses = db.execute(
        "SELECT DISTINCT course FROM materials WHERE course <> '' ORDER BY course ASC"
    ).fetchall()

    return render_template(
        "index.html",
        materials=materials,
        courses=[row["course"] for row in courses],
        q=q,
        selected_course=course,
        favorites_only=favorites_only,
    )


@bp.route("/materials/new", methods=["GET", "POST"])
def create_material():
    if request.method == "POST":
        data, errors = _validate_form(request.form)
        if not errors:
            db = get_db()
            db.execute(
                """
                INSERT INTO materials (title, url, course, tags, memo, favorite)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    data["title"],
                    data["url"],
                    data["course"],
                    data["tags"],
                    data["memo"],
                    data["favorite"],
                ),
            )
            db.commit()
            flash("教材を登録しました。", "success")
            return redirect(url_for("materials.index"))

        for error in errors:
            flash(error, "error")
        return render_template("form.html", material=data, is_edit=False)

    return render_template(
        "form.html",
        material={"title": "", "url": "", "course": "", "tags": "", "memo": "", "favorite": 0},
        is_edit=False,
    )


@bp.route("/materials/<int:material_id>/edit", methods=["GET", "POST"])
def edit_material(material_id: int):
    db = get_db()
    material = db.execute(
        "SELECT id, title, url, course, tags, memo, favorite FROM materials WHERE id = ?",
        (material_id,),
    ).fetchone()

    if material is None:
        flash("対象の教材が見つかりません。", "error")
        return redirect(url_for("materials.index"))

    if request.method == "POST":
        data, errors = _validate_form(request.form)
        if not errors:
            db.execute(
                """
                UPDATE materials
                   SET title = ?, url = ?, course = ?, tags = ?, memo = ?, favorite = ?
                 WHERE id = ?
                """,
                (
                    data["title"],
                    data["url"],
                    data["course"],
                    data["tags"],
                    data["memo"],
                    data["favorite"],
                    material_id,
                ),
            )
            db.commit()
            flash("教材を更新しました。", "success")
            return redirect(url_for("materials.index"))

        for error in errors:
            flash(error, "error")
        data["id"] = material_id
        return render_template("form.html", material=data, is_edit=True)

    return render_template("form.html", material=material, is_edit=True)


@bp.route("/materials/<int:material_id>/delete", methods=["POST"])
def delete_material(material_id: int):
    db = get_db()
    db.execute("DELETE FROM materials WHERE id = ?", (material_id,))
    db.commit()
    flash("教材を削除しました。", "success")
    return redirect(url_for("materials.index"))


@bp.route("/materials/<int:material_id>/toggle-favorite", methods=["POST"])
def toggle_favorite(material_id: int):
    db = get_db()
    material = db.execute("SELECT favorite FROM materials WHERE id = ?", (material_id,)).fetchone()
    if material is None:
        flash("対象の教材が見つかりません。", "error")
        return redirect(url_for("materials.index"))

    new_value = 0 if material["favorite"] else 1
    db.execute("UPDATE materials SET favorite = ? WHERE id = ?", (new_value, material_id))
    db.commit()
    flash("お気に入り状態を更新しました。", "success")
    return redirect(url_for("materials.index"))
