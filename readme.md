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
└── ui/
    └── auto-dbms-ui/             # Starter Angular 20 project (scaffolding only at present)
```

---

## Current Status

### Generator (`app/src/`) — mostly functional

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
| Config path is hard-coded in `main()` | ⚠️ Needs fix (`/home/daniel/…`) |
| `config.json` `fluff_config_path` is absolute | ⚠️ Needs to be made relative/configurable |

### Database (`db/`)

A `start_db.sh` script is provided that starts a PostgreSQL container via Docker. No migrations or seed data are included.

### UI (`ui/auto-dbms-ui/`) — scaffolding only

The Angular project was generated with Angular CLI 20 and currently contains only the default starter app. No API integration, routing, or Formly components have been implemented yet.

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

Edit `app/src/config/config.json` to set `fluff_config_path` to the absolute path of `app/src/config/.sqlfluff` on your machine, then:

```bash
cd app/src
python app.py
```

By default the generator reads `test.sql` in the same directory and writes output to an output directory of your choice.

### 4. Run the Angular UI

```bash
cd ui/auto-dbms-ui
npm install
ng serve
```

Open `http://localhost:4200/` in your browser.

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

- Hard-coded absolute path in `app/src/app.py` `main()` function (`config_path = '/home/daniel/…'`) — the generator must be configured via environment variable or CLI argument instead.
- `config.json` `fluff_config_path` is an absolute path that will not work on other machines — should default to a path relative to the config file.
- The `NoAuth` class in `template.py` currently references the `auth/blueprints_init.py.txt` template instead of a dedicated `noauth` version.
- The Angular UI (`ui/auto-dbms-ui/`) has no implementation yet — API integration and Formly rendering still need to be built.
- CherryPy is used as the WSGI server in generated projects; it may be preferable to use Gunicorn or the Flask dev server for simplicity.
