from utils import *
import sys
import os, shutil
from config import Config
from datetime import datetime

from templates.template import Templates
from utils.key_extractor.extractor_v2 import parse_sql_schema, format_output
import json

import logging

logging.basicConfig(level=logging.ERROR)
utils_logger = logging.getLogger('utils')
utils_logger.setLevel(logging.INFO)
logger = logging.getLogger(__name__)

def main():
    config_path = '/home/daniel/documents/auto_dbms/app/src/config/config.json'
    config = Config(config_file=config_path)
    sql_text = open('test.sql').read()
    
    # Validate SQL
    linter = SQLLinter()
    (valid, errors) = linter.validate_sql(sql_text)
    
    if not valid:
        for error in errors:
            logger.error(f"SQL Validation Error found - {error}")
        sys.exit(1)

    formatted_sql = linter.format_sql(sql_text)

    logger.info(f'Formatted SQL: {formatted_sql}')

    # models_sqlalchemy = convert_sql_to_sqlalchemy(formatted_sql)

    path = os.getcwd()
    logger.info(f'Current working directory: {path}')
    sample_path = os.path.join(os.path.dirname(path), 'sample_project')
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

    models = builder.convert(formatted_sql)

    tables = split_create_table_statements(formatted_sql)

    formly_converter = SqlToFormlyConverter()
    formly_schemas = {}
    table_formatter = TableSqlFormatter(config=config)

    bp_template = "app.register_blueprint({name}_blueprint, url_prefix='/api')   # Blueprint name is added to url in blueprint file\n"
    import_template = "from blueprints.{name}_blueprint import {name}_blueprint\n"

    blueprint_strs = []
    import_strs = []

    for table_sql in tables:
        formatted_table_sql = table_formatter.fix_table_sql(table_sql)
        schema = formly_converter.convert_to_json(formatted_table_sql, exclude_auto_increment=False)
        table_name = extract_table_name(formatted_table_sql)
        formly_schemas[table_name] = schema

        template_payload = {
            'name': table_name.lower(),
            'model_name': builder.to_camel_case(table_name)
        }

        Templates.form_template.write(forms_path, table_name.lower(), template_payload)
        Templates.service_template.write(services_path, table_name.lower(), template_payload)
        Templates.flask_blueprint.write(blueprints_path, table_name.lower(), template_payload)
        blueprint_strs.append(bp_template.format(**template_payload))
        import_strs.append(import_template.format(**template_payload))

    app_payload = {
        'blueprints': '    '.join(blueprint_strs),
        'imports': ''.join(import_strs)
    }

    Templates.extensions_template.write(sample_path, 'extensions', {})
    Templates.requirements_template.write(sample_path, 'requirements', {})
    Templates.app_template.write(sample_path, 'app', app_payload)
    Templates.config_template.write(sample_path, 'config', {})
    Templates.readme_template.write(sample_path, 'README', {
        'project_name': config.project_name,
        'files': len(os.listdir(blueprints_path)) + len(os.listdir(services_path)) + len(os.listdir(forms_path)) + 4,
        'tables': len(tables),
        'columns': 0,
        'user': os.getenv('USER') or 'unknown',
        'host': os.uname().nodename,
        'time': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })

    with open(os.path.join(sample_path, 'models.py'), 'w') as f:
        f.write(models)
    for table_name, schema in formly_schemas.items():
        with open(os.path.join(form_jsons_path, f'{table_name}_formly.json'), 'w') as f:
            f.write(schema)
    
    # Extract primary and foreign keys using key_extractor package
    logger.info("Extracting primary and foreign keys from SQL schema...")
    
    try:
        # Parse the SQL schema to extract key information
        key_extraction_results = parse_sql_schema(formatted_sql)
        
        # Create keys directory for output files
        keys_path = os.path.join(sample_path, 'keys')
        os.makedirs(keys_path, exist_ok=True)
        
        # Save detailed key information as JSON
        keys_json_path = os.path.join(keys_path, 'table_keys.json')
        with open(keys_json_path, 'w') as f:
            json.dump(key_extraction_results, f, indent=2)
        
        # Save human-readable format
        keys_report_path = os.path.join(keys_path, 'keys_report.txt')
        with open(keys_report_path, 'w') as f:
            f.write(format_output(key_extraction_results))
        
        logger.info(f"Key extraction completed successfully:")
        logger.info(f"  - JSON output: {keys_json_path}")
        logger.info(f"  - Report output: {keys_report_path}")
        logger.info(f"  - Found {len(key_extraction_results)} tables")
        
        # Log summary of extracted keys
        for table in key_extraction_results:
            pk_count = len(table.get('primary_keys', []))
            fk_count = len(table.get('foreign_keys', []))
            logger.info(f"  - Table '{table['table_name']}': {pk_count} primary key(s), {fk_count} foreign key(s)")
            
    except Exception as e:
        logger.error(f"Error during key extraction: {str(e)}")
        # Continue execution even if key extraction fails
    

if __name__ == '__main__':
    main()
