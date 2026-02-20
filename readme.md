# Auto DBMS

Auto DBMS from SQL is a code-generation tool that reads a SQL schema and produces a ready-to-run Flask REST API, along with the Formly JSON form definitions that an Angular front-end needs to render CRUD forms automatically. The goal is to make integrating with a legacy database as painless as possible: point the generator at an existing `CREATE TABLE` script and get a working back-end in seconds.

---

## Project Goals

1. **SQL-in → Flask API out** – parse any `CREATE TABLE` SQL schema and emit a complete Flask/SQLAlchemy project.
2. **Auto-CRUD routes** – every table gets `get_all`, `get`, `add`, `update`, and `delete` endpoints automatically.
3. **Form definitions** – every table also exposes a `form-data` endpoint that returns a [Formly](https://formly.dev/) JSON schema so the front-end can render the correct input form without hard-coding anything.
4. **`/api/get_all` discovery route** – a `db_models` blueprint returns a list of every generated table (name + path) so the UI can build its navigation dynamically.
5. **Auth and no-auth flavours** – the generator can produce either a plain Flask app (`noauth`) or one secured with [Flask-JWT-Extended](https://flask-jwt-extended.readthedocs.io/) and [Flask-Bcrypt](https://flask-bcrypt.readthedocs.io/) (`auth`).
6. **Angular UI** – a starter Angular project lives in `ui/auto-dbms-ui/` that is intended to consume the generated API and render forms automatically.

---

## Repository Layout

```
auto_dbms_from_sql/
├── app/
│   ├── requirements.txt          # Python deps for the generator itself
│   └── src/
│       ├── app.py                # Main generator entry-point (AutoDBMS class + main())
│       ├── config/               # Config loader (Config.py) and config.json
│       ├── templates/            # Jinja/string-template files used during generation
│       │   ├── noauth/           # Templates for the no-auth flavour
│       │   │   ├── basic/        # Blueprint + service for tables without full PK info
│       │   │   └── fullcrud/     # Blueprint + service for full CRUD tables
│       │   └── auth/             # Templates for the JWT-auth flavour (same structure)
│       └── utils/                # SQL parsing, linting, SQLAlchemy + Formly converters
├── db/
│   └── start_db.sh               # Docker one-liner to spin up a local PostgreSQL instance
├── tests/
│   ├── conftest.py               # Shared pytest fixtures (Docker, Flask server, Playwright)
│   ├── requirements.txt          # Test dependencies
│   ├── sample_schema.sql         # 4-table SQL schema used by the test suite
│   ├── test_pipeline.py          # BDD step definitions for pipeline.feature
│   ├── test_crud.py              # BDD step definitions for crud.feature (UI)
│   └── features/                 # Gherkin feature files
└── ui/
    └── auto-dbms-ui/             # Angular 20 UI – entity list, detail, CRUD panels, auth
```

---

## Current Status

### Generator (`app/src/`) — functional

| Feature | Status |
|---|---|
| SQL validation & formatting (sqlfluff) | ✅ Working |
| SQLAlchemy model generation | ✅ Working |
| Formly JSON schema generation | ✅ Working |
| No-auth Flask project output | ✅ Working |
| Auth (JWT) Flask project output | ✅ Working |
| `db_models` discovery route (`/api/get_all`) | ✅ Working |
| Per-table `form-data` route | ✅ Working |
| Full CRUD routes per table | ✅ Working |
| Config path (relative / env-var override) | ✅ Fixed |
| `config.json` `fluff_config_path` (relative) | ✅ Fixed |
| CLI flags (`--config`, `--sql`, `--output`, `--auth`) | ✅ Working |

### Database (`db/`)

A `start_db.sh` script is provided that starts a PostgreSQL container via Docker. No migrations or seed data are included.

### UI (`ui/auto-dbms-ui/`) — functional

The Angular 20 project is wired up to the generated API and provides a working CRUD interface:

| Feature | Status |
|---|---|
| Entity list page (fetches `/api/get_all` dynamically) | ✅ Working |
| Entity detail page with 5 CRUD operation panels | ✅ Working |
| Navbar component | ✅ Working |
| `EntityService` (get-all, get-one, add, update, delete, form-data) | ✅ Working |
| `AuthService` + JWT auth interceptor | ✅ Working |
| Routing (`/` → entity list, `/entity/:name` → detail) | ✅ Working |

### Tests (`tests/`)

A pytest-bdd test suite covers the full pipeline:

| Test | Coverage |
|---|---|
| `features/pipeline.feature` | Project file generation, API entity list, add/delete records |
| `features/crud.feature` | UI CRUD operations via Playwright (opt-in with `--run-ui`) |
| `features/auth.feature` | Login/logout flows via UI (opt-in with `--run-ui`) |

---

## Quick Start

### 1. Start the database

```bash
cd db
bash start_db.sh
```

### 2. Install generator dependencies

```bash
cd app
pip install -r requirements.txt
```

### 3. Run the generator

```bash
cd app/src
python app.py [--sql path/to/schema.sql] [--output path/to/output_dir] [--config path/to/config.json]
```

All arguments are optional. By default the generator reads `test.sql` in the same directory and writes output to `../sample_project`. The config file path can also be set via the `app_config_file` environment variable.

### 4. Run the Angular UI

```bash
cd ui/auto-dbms-ui
npm install
ng serve
```

Open `http://localhost:4200/` in your browser.

---

## Testing

The `tests/` directory contains a pytest-bdd suite that exercises the full pipeline using real Docker containers via `testcontainers`.

### Install test dependencies

```bash
cd tests
pip install -r requirements.txt
```

### Run the pipeline tests (no browser required)

```bash
cd tests
pytest test_pipeline.py -v
```

### Run UI/Playwright tests (opt-in)

```bash
cd tests
pytest test_crud.py --run-ui -v
```

---

## Generated API Routes

For each table `<table>` in the schema the generator produces:

| Method | Path | Description |
|---|---|---|
| `GET` | `/api/<table>/get_all` | Return all rows |
| `GET` | `/api/<table>/get/<pk>` | Return a single row by primary key |
| `POST` | `/api/<table>/add` | Insert a new row (JSON body) |
| `POST` | `/api/<table>/update/<pk>` | Update a row by primary key (JSON body) |
| `DELETE` | `/api/<table>/delete/<pk>` | Delete a row by primary key |
| `GET` | `/api/<table>/form-data` | Return the Formly schema for this table |

Plus the discovery route:

| Method | Path | Description |
|---|---|---|
| `GET` | `/api/get_all` | Return a list of all tables with their API paths |

---

## Known Issues / TODO

- CherryPy is used as the WSGI server in generated projects; it may be preferable to use Gunicorn or the Flask dev server for simplicity.
- ~~The `form-data` endpoint is defined in the Formly templates but is not yet wired into the Angular UI.~~ **Fixed**: `EntityService` now exposes a `getFormData()` method and a "Form Data" panel appears on each entity's detail page.
- ~~Auth (JWT) flavour templates exist in `app/src/templates/auth/` but the generator currently always produces no-auth output; a CLI flag to select the auth flavour is not yet implemented.~~ **Fixed**: pass `--auth` to the generator to produce a JWT-secured project.
