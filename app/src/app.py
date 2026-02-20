from utils import *
import sys
import os, shutil
import argparse
from config import Config
from datetime import datetime

from templates.template import Templates
from utils.key_extractor.extractor_v2 import parse_sql_schema, format_output
from config.Config import Config
import json

import logging

#region Load Configuration

cfg_env = os.getenv('app_config_file', None)
config = Config(config_file=os.path.join(os.path.dirname(__file__), 'config', 'config.json') if cfg_env is None else cfg_env)

#endregion

#region Logging Setup

# Apply config.logging_config to logging
def apply_logging_config(logging_config, name=__name__):
    log = logging.getLogger(name)
    level = getattr(logging, logging_config.level.name, logging.INFO)
    log.setLevel(level)
    handler = logging.StreamHandler()
    formatter = logging.Formatter(logging_config.format)
    handler.setFormatter(formatter)
    log.addHandler(handler)
    
    if logging_config.file_path:
        file_handler = logging.FileHandler(logging_config.file_path)
        file_handler.setFormatter(formatter)
        log.addHandler(file_handler)
    
    return log

log = apply_logging_config(config.logging_config)
for module_name, module_log_config in config.module_logging.items():
    apply_logging_config(module_log_config, name=module_name)

#endregion

# Constants

sqlalchemy_to_python_types = {
    'Integer': 'int',
    'SmallInteger': 'int',
    'BigInteger': 'int',
    'String': 'str',
    'Text': 'str',
    'Boolean': 'bool',
    'Date': 'datetime.date',
    'DateTime': 'datetime.datetime',
    'Time': 'datetime.time',
    'Float': 'float',
    'Numeric': 'float',
    'LargeBinary': 'str',
    'JSON': 'str',
}

#endregion

class AutoDBMS():
    
    def __init__(self, config):
        self.config = config
        self.linter = SQLLinter()
        self.flask_sqlalchemy_builder = SQLToFlaskSQLAlchemy()
        self.formly_converter = SqlToFormlyConverter()
        self.table_formatter = TableSqlFormatter(config=config)
        
    def sql_is_valid(self, sql_text: str) -> bool:
        return self.linter.validate_sql(sql_text)[0]
    
    def get_sql_errors(self, sql_text: str) -> list:
        return self.linter.validate_sql(sql_text)[1]
    
    def format_sql(self, sql_text: str) -> str:
        return self.linter.format_sql(sql_text)
    
    
    
    def main(self, sql: str):
        if not self.sql_is_valid(sql):
            errors = self.get_sql_errors(sql)
            for error in errors:
                log.error(f"SQL Validation Error found - {error}")
            sys.exit(1)

        formatted_sql = self.format_sql(sql)
        log.info(f'Formatted SQL: {formatted_sql}')

        models, tables_dict = self.flask_sqlalchemy_builder.convert(formatted_sql)
        table_dict_keys = list(tables_dict.keys())

        tables = split_create_table_statements(formatted_sql)

        formly_schemas = {}

        for table_sql in tables:
            formatted_table_sql = self.table_formatter.fix_table_sql(table_sql)
            schema = self.formly_converter.convert_to_json(formatted_table_sql, exclude_auto_increment=False)
            table_name = extract_table_name(formatted_table_sql).strip().lower()
            formly_schemas[table_name] = schema

        return {
            'models': models,
            'tables_dict': tables_dict,
            'formly_schemas': formly_schemas
        }
    
def generate_project(sql_text: str, output_dir: str, config, use_auth: bool = False) -> None:
    """Generate a Flask DBMS project from SQL text and write files to output_dir."""
    linter = SQLLinter()
    (valid, errors) = linter.validate_sql(sql_text)

    if not valid:
        for error in errors:
            log.error(f"SQL Validation Error found - {error}")
        raise ValueError(f"SQL validation failed: {errors}")

    formatted_sql = linter.format_sql(sql_text)
    log.info(f'Formatted SQL: {formatted_sql}')

    sample_path = output_dir
    services_path = os.path.join(sample_path, 'services')
    forms_path = os.path.join(sample_path, 'forms')
    form_jsons_path = os.path.join(forms_path, 'json')
    blueprints_path = os.path.join(sample_path, 'blueprints')

    if os.path.exists(sample_path):
        shutil.rmtree(sample_path)
    os.makedirs(sample_path)
    os.makedirs(services_path)
    os.makedirs(forms_path)
    os.makedirs(blueprints_path)
    os.makedirs(form_jsons_path)

    builder = SQLToFlaskSQLAlchemy()

    models, tables_dict = builder.convert(formatted_sql)
    table_dict_keys = list(tables_dict.keys())

    tables = split_create_table_statements(formatted_sql)

    formly_converter = SqlToFormlyConverter()
    formly_schemas = {}
    table_formatter = TableSqlFormatter(config=config)

    # Entity blueprints use their own /api/{name} url_prefix (set in the blueprint file).
    # Only db_models needs an explicit url_prefix on registration.
    bp_template = "app.register_blueprint({name}_blueprint)\n"
    import_template = "from blueprints.{name}_blueprint import {name}_blueprint\n"

    blueprint_strs = []
    import_strs = []
    all_models = []

    for table_sql in tables:
        formatted_table_sql = table_formatter.fix_table_sql(table_sql)
        schema = formly_converter.convert_to_json(formatted_table_sql, exclude_auto_increment=False)
        table_name = extract_table_name(formatted_table_sql).strip().lower()
        formly_schemas[table_name] = schema

        table_name_camel = builder.to_camel_case(table_name)
        all_models.append({'name': table_name_camel, 'path': f'/{table_name}'})

        if table_name not in table_dict_keys:
            log.error(f"Table {table_name} not found in sql -> flask_sqlalchemy converter parsed tables, only basic get_all functionality will be created.")

            template_payload = {
                'name': table_name,
                'model_name': table_name_camel
            }

            Templates.form_template.write(forms_path, table_name, template_payload)
            if use_auth:
                Templates.Auth.Basic.service_template.write(services_path, table_name, template_payload)
                Templates.Auth.Basic.flask_blueprint.write(blueprints_path, table_name, template_payload)
            else:
                Templates.NoAuth.Basic.service_template.write(services_path, table_name, template_payload)
                Templates.NoAuth.Basic.flask_blueprint.write(blueprints_path, table_name, template_payload)
            blueprint_strs.append(bp_template.format(**template_payload))
            import_strs.append(import_template.format(**template_payload))

        else:
            log.info(f"Generating full CRUD for table {table_name}.")

            template_payload = {
                'name': table_name,
                'model_name': table_name_camel
            }

            table_rec = tables_dict.get(table_name, None)
            crud_inputs = []
            crud_inputs_typed = []
            url_params = []
            pk_filter = []
            add_payload = []
            update_payload = []
            # build crud inputs
            for column in table_rec.get('columns', []):
                add_payload.append(f"        {column['name']}= payload.get('{column['name']}', None)")
                if not column.get('primary_key', False):
                    # Skip non pk columns for update
                    update_payload.append(f"    if '{column['name']}' in payload:\n        rec.{column['name']} = payload.get('{column['name']}')")
                    continue

                python_type = sqlalchemy_to_python_types.get(column.get('type', 'String'), 'str')
                cn_l = column['name'].lower()
                crud_inputs.append(f'{cn_l}')
                crud_inputs_typed.append(f'{cn_l}: {python_type}')
                url_params.append(f'<{python_type}:{cn_l}>')
                pk_filter.append(f'{template_payload["model_name"]}.{cn_l} == {cn_l}')

            template_payload['add_payload'] = ',\n'.join(add_payload)
            template_payload['update_payload'] = '\n'.join(update_payload)
            template_payload['pk_id_filter'] = ' & '.join(pk_filter)

            if len(crud_inputs) > 1:
                template_payload['crud_keys'] = ', '.join(crud_inputs)
                template_payload['crud_route'] = '/'.join(url_params)
                template_payload['crud_keys_typed'] = ', '.join(crud_inputs_typed)
            elif len(crud_inputs) == 1:
                template_payload['crud_keys'] = crud_inputs[0]
                template_payload['crud_route'] = url_params[0]
                template_payload['crud_keys_typed'] = crud_inputs_typed[0]

            Templates.form_template.write(forms_path, table_name, template_payload)
            if use_auth:
                Templates.Auth.FullCrud.service_template.write(services_path, table_name, template_payload)
                Templates.Auth.FullCrud.flask_blueprint.write(blueprints_path, table_name, template_payload)
            else:
                Templates.NoAuth.FullCrud.service_template.write(services_path, table_name, template_payload)
                Templates.NoAuth.FullCrud.flask_blueprint.write(blueprints_path, table_name, template_payload)
            blueprint_strs.append(bp_template.format(**template_payload))
            import_strs.append(import_template.format(**template_payload))

    db_models_payload = {
        'payload': all_models
    }
    if use_auth:
        Templates.Auth.db_models_blueprint.write(blueprints_path, 'db_models', db_models_payload)
    else:
        Templates.NoAuth.db_models_blueprint.write(blueprints_path, 'db_models', db_models_payload)
    # db_models blueprint has no url_prefix so it needs one at registration time
    blueprint_strs.append("app.register_blueprint(db_models_blueprint, url_prefix='/api')\n")
    import_strs.append(import_template.format(name='db_models'))

    if use_auth:
        blueprint_strs.append("app.register_blueprint(auth_blueprint)\n")
        import_strs.append("from blueprints.auth_blueprint import auth_blueprint\n")

    app_payload = {
        'blueprints': '    '.join(blueprint_strs),
        'imports': ''.join(import_strs)
    }

    # 6 core files: app.py, extensions.py, requirements.txt, config.py, README.md, models.py
    GENERATED_CORE_FILES = 6
    readme_payload = {
        'project_name': config.project_name,
        'files': len(os.listdir(blueprints_path)) + len(os.listdir(services_path)) + len(os.listdir(forms_path)) + GENERATED_CORE_FILES,
        'tables': len(tables),
        'columns': 0,
        'user': os.getenv('USER') or 'unknown',
        'host': os.uname().nodename,
        'time': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    if use_auth:
        Templates.Auth.extensions_template.write(sample_path, 'extensions', {})
        Templates.Auth.requirements_template.write(sample_path, 'requirements', {})
        Templates.Auth.app_template.write(sample_path, 'app', app_payload)
        Templates.Auth.config_template.write(sample_path, 'config', {})
        Templates.Auth.blueprints_init_template.write(blueprints_path, '__init__', {})
        Templates.Auth.readme_template.write(sample_path, 'README', readme_payload)
        Templates.Auth.auth_blueprint.write(blueprints_path, 'auth', {})
        Templates.Auth.user_model.write(sample_path, 'user_model', {})
    else:
        Templates.NoAuth.extensions_template.write(sample_path, 'extensions', {})
        Templates.NoAuth.requirements_template.write(sample_path, 'requirements', {})
        Templates.NoAuth.app_template.write(sample_path, 'app', app_payload)
        Templates.NoAuth.config_template.write(sample_path, 'config', {})
        Templates.NoAuth.blueprints_init_template.write(blueprints_path, '__init__', {})
        Templates.NoAuth.readme_template.write(sample_path, 'README', readme_payload)

    with open(os.path.join(sample_path, 'models.py'), 'w') as f:
        f.write(models)
    for table_name, schema in formly_schemas.items():
        with open(os.path.join(form_jsons_path, f'{table_name}_formly.json'), 'w') as f:
            f.write(schema)

    # __init__.py files
    open(os.path.join(services_path, '__init__.py'), 'a').close()
    open(os.path.join(forms_path, '__init__.py'), 'a').close()
    open(os.path.join(sample_path, '__init__.py'), 'a').close()


def main():
    parser = argparse.ArgumentParser(description='Auto DBMS generator')
    parser.add_argument('--config', default=None, help='Path to config.json')
    parser.add_argument('--sql', default=None, help='Path to SQL file (default: test.sql)')
    parser.add_argument('--output', default=None, help='Output directory (default: ../sample_project)')
    parser.add_argument('--auth', action='store_true', default=False, help='Generate JWT-auth flavour (default: no-auth)')
    args = parser.parse_args()
    config_path = args.config or os.getenv('app_config_file', os.path.join(os.path.dirname(__file__), 'config', 'config.json'))
    config = Config(config_file=config_path)
    sql_file = args.sql or 'test.sql'
    sql_text = open(sql_file).read()

    output_dir = args.output or os.path.join(os.path.dirname(os.getcwd()), 'sample_project')
    generate_project(sql_text, output_dir, config, use_auth=args.auth)

if __name__ == '__main__':
    main()
