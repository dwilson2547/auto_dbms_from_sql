"""
pytest-bdd step definitions for features/pipeline.feature.

Tests cover:
  - Project file generation from a SQL schema
  - The generated API returning entities and supporting CRUD operations
"""
import os

import pytest
import requests
from pytest_bdd import given, parsers, scenarios, then, when

from conftest import SAMPLE_SCHEMA

scenarios("features/pipeline.feature")

# ---------------------------------------------------------------------------
# State shared across steps within a single scenario
# ---------------------------------------------------------------------------


@pytest.fixture
def ctx():
    """Mutable dict used to pass state between step functions."""
    return {}


# ---------------------------------------------------------------------------
# Given steps
# ---------------------------------------------------------------------------


@given("the sample schema with 4 tables", target_fixture="sql_text")
def sql_text():
    return SAMPLE_SCHEMA.read_text()


@given("a running PostgreSQL test database")
def running_postgres(postgres_container):
    # fixture already started by conftest; nothing extra needed here
    pass


# ---------------------------------------------------------------------------
# When steps
# ---------------------------------------------------------------------------


@when("I generate a project from the sample schema", target_fixture="project_path")
def project_path(generated_project_path):
    return generated_project_path


@when("the generated Flask API is running")
def flask_api_running(flask_server):
    # fixture started by conftest; just confirm it's reachable
    resp = requests.get(f"{flask_server}/api/get_all", timeout=5)
    assert resp.status_code == 200, f"Flask API /api/get_all returned {resp.status_code}"


@when(
    parsers.parse('I POST a customer with name "{name}" and email "{email}"'),
    target_fixture="added_customer",
)
def post_customer(flask_server, name, email):
    resp = requests.post(
        f"{flask_server}/api/customers/add",
        json={"name": name, "email": email},
        timeout=5,
    )
    assert resp.status_code == 200, f"POST /api/customers/add returned {resp.status_code}: {resp.text}"
    return resp.json()


@when(parsers.parse('I DELETE the customer with id "{customer_id}"'))
def delete_customer(flask_server, customer_id):
    resp = requests.delete(
        f"{flask_server}/api/customers/delete/{customer_id}",
        timeout=5,
    )
    assert resp.status_code == 200, f"DELETE returned {resp.status_code}: {resp.text}"


@then("the customer can be deleted by its returned id")
def delete_added_customer(flask_server, added_customer):
    cid = added_customer["id"]
    resp = requests.delete(
        f"{flask_server}/api/customers/delete/{cid}",
        timeout=5,
    )
    assert resp.status_code == 200, f"DELETE returned {resp.status_code}: {resp.text}"


@then(parsers.parse('GET /api/customers/get_all does not contain name "{name}"'))
def customers_does_not_contain(flask_server, name):
    resp = requests.get(f"{flask_server}/api/customers/get_all", timeout=5)
    assert resp.status_code == 200
    names = [r.get("name") for r in resp.json()]
    assert name not in names, f'"{name}" was unexpectedly found in customers: {names}'


# ---------------------------------------------------------------------------
# Then steps – project file structure
# ---------------------------------------------------------------------------


@then("a models.py file is created")
def models_file_created(project_path):
    assert (project_path / "models.py").exists(), "models.py was not generated"


@then("an app.py file is created")
def app_file_created(project_path):
    assert (project_path / "app.py").exists(), "app.py was not generated"


@then("a blueprint file is created for each of the 4 tables")
def blueprint_files_created(project_path):
    expected = {"customers_blueprint.py", "products_blueprint.py", "orders_blueprint.py", "order_items_blueprint.py"}
    found = {f.name for f in (project_path / "blueprints").iterdir() if f.suffix == ".py"}
    missing = expected - found
    assert not missing, f"Missing blueprint files: {missing}"


@then("a service file is created for each of the 4 tables")
def service_files_created(project_path):
    expected = {"customers_service.py", "products_service.py", "orders_service.py", "order_items_service.py"}
    found = {f.name for f in (project_path / "services").iterdir() if f.suffix == ".py"}
    missing = expected - found
    assert not missing, f"Missing service files: {missing}"


@then("a form file is created for each of the 4 tables")
def form_files_created(project_path):
    expected = {"customers_form.py", "products_form.py", "orders_form.py", "order_items_form.py"}
    found = {f.name for f in (project_path / "forms").iterdir() if f.suffix == ".py"}
    missing = expected - found
    assert not missing, f"Missing form files: {missing}"


# ---------------------------------------------------------------------------
# Then steps – API responses
# ---------------------------------------------------------------------------


@then("GET /api/get_all returns 4 entities", target_fixture="entity_list")
def entity_list_has_4(flask_server):
    resp = requests.get(f"{flask_server}/api/get_all", timeout=5)
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 4, f"Expected 4 entities, got {len(data)}: {data}"
    return data


@then(parsers.parse('the entity list includes "{entity_name}"'))
def entity_list_includes(entity_list, entity_name):
    names = [e["name"] for e in entity_list]
    assert entity_name in names, f'"{entity_name}" not found in entity list: {names}'


@then(parsers.parse('GET /api/customers/get_all returns a record with name "{name}"'))
def customers_contains_name(flask_server, name):
    resp = requests.get(f"{flask_server}/api/customers/get_all", timeout=5)
    assert resp.status_code == 200
    records = resp.json()
    names = [r.get("name") for r in records]
    assert name in names, f'"{name}" not found in customers: {names}'
