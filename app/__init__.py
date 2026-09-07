"""Application factory."""

from __future__ import annotations

from flask import Flask, render_template

from app.blueprints.learn import learn_bp
from app.blueprints.site import site_bp
from app.config import Config
from app.content.registry import load_curriculum
from app.markup import inline_code


def create_app(config: Config | None = None) -> Flask:
    app = Flask(__name__)
    app.config.from_mapping((config or Config()).as_dict())

    app.register_blueprint(site_bp)
    app.register_blueprint(learn_bp)

    app.jinja_env.filters["inline_code"] = inline_code

    _register_context(app)
    _register_error_handlers(app)
    return app


def _register_context(app: Flask) -> None:
    curriculum = load_curriculum()

    @app.context_processor
    def inject_globals() -> dict[str, object]:
        return {
            "site_name": app.config["SITE_NAME"],
            "site_tagline": app.config["SITE_TAGLINE"],
            "chapters": curriculum.chapters,
            "lesson_total": curriculum.lesson_count,
        }


def _register_error_handlers(app: Flask) -> None:
    @app.errorhandler(404)
    def not_found(_error: object) -> tuple[str, int]:
        return render_template("errors/404.html"), 404

    @app.errorhandler(500)
    def server_error(_error: object) -> tuple[str, int]:
        return render_template("errors/500.html"), 500
