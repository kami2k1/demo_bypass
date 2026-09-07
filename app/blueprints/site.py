"""Các trang chung: trang chủ, giới thiệu, tìm kiếm, demo, sitemap."""

from __future__ import annotations

from flask import (
    Blueprint,
    Response,
    abort,
    current_app,
    render_template,
    request,
    url_for,
)

from app.content.registry import load_curriculum
from app.search import search

site_bp = Blueprint("site", __name__)


@site_bp.route("/")
def home() -> str:
    curriculum = load_curriculum()
    return render_template(
        "home.html",
        curriculum=curriculum,
        featured=curriculum.featured(6),
        top_tags=curriculum.tag_counts()[:12],
        demos=curriculum.demos[:4],
    )


@site_bp.route("/tai-sao-go")
def why_go() -> str:
    curriculum = load_curriculum()
    return render_template("why_go.html", curriculum=curriculum)


@site_bp.route("/gioi-thieu")
def about() -> str:
    return render_template("about.html", curriculum=load_curriculum())


@site_bp.route("/tim-kiem")
def search_page() -> str:
    query = request.args.get("q", "", type=str).strip()
    limit = current_app.config["MAX_SEARCH_RESULTS"]
    hits = search(query, limit=limit) if query else ()
    return render_template("search.html", query=query, hits=hits)


@site_bp.route("/demos")
def demo_index() -> str:
    curriculum = load_curriculum()
    return render_template("demo_index.html", demos=curriculum.demos, curriculum=curriculum)


@site_bp.route("/demos/<slug>")
def demo_detail(slug: str) -> str:
    curriculum = load_curriculum()
    demo = curriculum.demo(slug)
    if demo is None:
        abort(404)
    return render_template(
        "demo_detail.html",
        demo=demo,
        lesson=curriculum.lesson(demo.related_lesson),
    )


@site_bp.route("/sitemap")
def sitemap() -> str:
    return render_template("sitemap.html", curriculum=load_curriculum())


@site_bp.route("/sitemap.xml")
def sitemap_xml() -> Response:
    curriculum = load_curriculum()
    paths = [
        url_for("site.home"),
        url_for("site.why_go"),
        url_for("site.about"),
        url_for("site.demo_index"),
        url_for("learn.curriculum"),
        url_for("learn.tag_index"),
    ]
    paths += [url_for("learn.chapter_detail", slug=c.slug) for c in curriculum.chapters]
    paths += [url_for("learn.lesson_detail", slug=lesson.slug) for lesson in curriculum.lessons]
    paths += [url_for("learn.tag_detail", tag=tag) for tag in curriculum.tags]
    paths += [url_for("site.demo_detail", slug=d.slug) for d in curriculum.demos]

    body = render_template("sitemap.xml", paths=paths, base=request.url_root.rstrip("/"))
    return Response(body, mimetype="application/xml")
