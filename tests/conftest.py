from __future__ import annotations

import pytest
from flask import Flask
from flask.testing import FlaskClient

from app import create_app
from app.config import TestingConfig
from app.content.registry import Curriculum, load_curriculum


@pytest.fixture(scope="session")
def app() -> Flask:
    return create_app(TestingConfig())


@pytest.fixture()
def client(app: Flask) -> FlaskClient:
    return app.test_client()


@pytest.fixture(scope="session")
def curriculum() -> Curriculum:
    return load_curriculum()
