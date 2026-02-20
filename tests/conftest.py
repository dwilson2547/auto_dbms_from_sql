"""
Shared fixtures for the AutoDBMS Gherkin test suite.

Session-scoped fixtures handle expensive setup (Docker container, project
generation, Flask server, Angular UI) so they are started once per test
session and reused across scenarios.

UI tests (Playwright) are opt-in: pass --run-ui to pytest to enable them.
"""
import json
import os
import socket
import subprocess
import sys
import time
from pathlib import Path

import pytest
import requests

# ---------------------------------------------------------------------------
# Path setup – make app/src importable
# ---------------------------------------------------------------------------
ROOT_DIR = Path(__file__).resolve().parent.parent
APP_SRC = ROOT_DIR / "app" / "src"
if str(APP_SRC) not in sys.path:
    sys.path.insert(0, str(APP_SRC))

SAMPLE_SCHEMA = Path(__file__).resolve().parent / "sample_schema.sql"
UI_DIR = ROOT_DIR / "ui" / "auto-dbms-ui"
APP_CONFIG = APP_SRC / "config" / "config.json"


def _free_port() -> int:
    """Return an unused TCP port on the local machine."""
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


# ---------------------------------------------------------------------------
# CLI option
# ---------------------------------------------------------------------------
def pytest_addoption(parser: pytest.Parser) -> None:
    parser.addoption(
        "--run-ui",
        action="store_true",
        default=False,
        help="Run UI/Playwright tests (requires ng serve and a Playwright browser)",
    )


# ---------------------------------------------------------------------------
# Core fixtures
# ---------------------------------------------------------------------------


@pytest.fixture(scope="session")
def postgres_container():
    """Start a PostgreSQL testcontainer and yield connection parameters."""
    from testcontainers.postgres import PostgresContainer

    with PostgresContainer("postgres:15") as pg:
        yield {
            "host": pg.get_container_host_ip(),
            "port": pg.get_exposed_port(5432),
            "username": pg.username,
            "password": pg.password,
            "dbname": pg.dbname,
        }


@pytest.fixture(scope="session")
def generated_project_path(tmp_path_factory):
    """
    Generate a Flask DBMS project from sample_schema.sql into a temporary
    directory using the same logic as app/src/app.py generate_project().
    Returns the Path to the generated project root.
    """
    from app import generate_project
    from config.Config import Config

    config = Config(config_file=str(APP_CONFIG))
    sql_text = SAMPLE_SCHEMA.read_text()

    project_dir = tmp_path_factory.mktemp("generated_project")
    generate_project(sql_text, str(project_dir), config)
    return project_dir


@pytest.fixture(scope="session")
def flask_server(generated_project_path, postgres_container):
    """
    Start the generated Flask API server against the test PostgreSQL container.
    Yields the base URL of the running server.
    """
    db = postgres_container
    db_url = f"{db['host']}:{db['port']}"
    port = _free_port()
    env = {
        **os.environ,
        "FLASK_APP": "app.py",
        "FLASK_ENV": "development",
        "db_url": db_url,
        "db_user": db["username"],
        "db_pass": db["password"],
        "db_name": db["dbname"],
        "db_type": "postgres",
    }

    proc = subprocess.Popen(
        [sys.executable, "-m", "flask", "run", "--port", str(port), "--no-debugger"],
        env=env,
        cwd=str(generated_project_path),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    base_url = f"http://localhost:{port}"
    _wait_for_http(f"{base_url}/api/get_all", timeout=30)

    yield base_url

    proc.terminate()
    try:
        proc.wait(timeout=5)
    except subprocess.TimeoutExpired:
        proc.kill()


@pytest.fixture(scope="session")
def angular_ui_url(request, flask_server, tmp_path_factory):
    """
    Start the Angular dev server with a proxy pointing to the Flask API.
    Skipped unless --run-ui is passed.  Yields the UI base URL.
    """
    if not request.config.getoption("--run-ui"):
        pytest.skip("UI tests disabled – pass --run-ui to enable")
    proxy_config = {
        "/api": {
            "target": flask_server,
            "secure": False,
            "changeOrigin": True,
        }
    }
    proxy_path = tmp_path_factory.mktemp("proxy") / "proxy.conf.json"
    proxy_path.write_text(json.dumps(proxy_config))

    port = _free_port()
    proc = subprocess.Popen(
        [
            "npx",
            "ng",
            "serve",
            "--port",
            str(port),
            "--proxy-config",
            str(proxy_path),
            "--no-live-reload",
        ],
        cwd=str(UI_DIR),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    ui_url = f"http://localhost:{port}"
    _wait_for_http(ui_url, timeout=120)

    yield ui_url

    proc.terminate()
    try:
        proc.wait(timeout=10)
    except subprocess.TimeoutExpired:
        proc.kill()


# ---------------------------------------------------------------------------
# Playwright fixtures
# ---------------------------------------------------------------------------


@pytest.fixture(scope="session")
def playwright_browser(request):
    """
    Launch a headless Chromium browser for the test session.
    Skipped unless --run-ui is passed.
    """
    if not request.config.getoption("--run-ui"):
        pytest.skip("UI tests disabled – pass --run-ui to enable")

    from playwright.sync_api import sync_playwright

    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True)
        yield browser
        browser.close()


@pytest.fixture
def page(playwright_browser, angular_ui_url):
    """
    Open a new browser page for each test function.
    The page navigates to the Angular UI base URL.
    """
    pg = playwright_browser.new_page()
    pg.set_default_timeout(15_000)
    yield pg
    pg.close()


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------


def _wait_for_http(url: str, timeout: int = 30) -> None:
    """Poll *url* until it responds with any HTTP status or until *timeout* seconds."""
    deadline = time.time() + timeout
    last_exc: Exception | None = None
    while time.time() < deadline:
        try:
            requests.get(url, timeout=2)
            return
        except Exception as exc:
            last_exc = exc
            time.sleep(1)
    raise RuntimeError(
        f"Service at {url} did not become ready within {timeout}s – last error: {last_exc}"
    )
