from string import Template
import os
import logging

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

class TemplateFile():
    """Class representing a template file with its content and filename."""
    
    def __init__(self, filename: str, name_template: str):
        self.filename = filename
        self.content = self.load_content()
        self.name_template = name_template

    def load_content(self) -> str:
        path = os.path.join(os.path.dirname(__file__), self.filename)
        """Load the content of the template file."""
        with open(path, 'r') as file:
            log.info(f'Loaded template file: {path}')
            return file.read()
    
    def gen_name(self, name: str) -> str:
        """Generate the output filename by substituting variables from context."""
        template = Template(self.name_template)
        return template.substitute({'name': name})
    
    def write(self, output_dir: str, name: str, context: dict):
        """Write the template content to the specified output path, substituting variables from context."""
        template = Template(self.content)
        rendered_content = template.substitute(context)
        
        log.info(f'Writing file: {os.path.join(output_dir, self.gen_name(name))}')

        with open(os.path.join(output_dir, self.gen_name(name)), 'w') as file:
            file.write(rendered_content)

class Templates:
    class Static:
        bp_template = "app.register_blueprint({name}_blueprint, url_prefix='/api')   # Blueprint name is added to url in blueprint file\n"
        import_template = "from blueprints.{name}_blueprint import {name}_blueprint\n"
    form_template = TemplateFile('form_blueprint.py.txt', '${name}_form.py')
    class Auth:
        blueprints_init_template = TemplateFile('auth/blueprints_init.py.txt', '__init__.py')
        extensions_template = TemplateFile('auth/extensions.py.txt', 'extensions.py')
        app_template = TemplateFile('auth/app.py.txt', 'app.py')
        requirements_template = TemplateFile('auth/requirements.txt.txt', 'requirements.txt')
        config_template = TemplateFile('auth/config.py.txt', 'config.py')
        readme_template = TemplateFile('auth/README.md.txt', 'README.md')
        db_models_blueprint = TemplateFile('auth/db_models_blueprint.py.txt', 'db_models_blueprint.py')
        class Basic:
            flask_blueprint = TemplateFile('auth/basic/flask_blueprint.py.txt', '${name}_blueprint.py')
            service_template = TemplateFile('auth/basic/service_template.py.txt', '${name}_service.py')
        class FullCrud:
            flask_blueprint = TemplateFile('auth/fullcrud/flask_blueprint.py.txt', '${name}_blueprint.py')
            service_template = TemplateFile('auth/fullcrud/service_template.py.txt', '${name}_service.py')
    class NoAuth:
        blueprints_init_template = TemplateFile('auth/blueprints_init.py.txt', '__init__.py')
        extensions_template = TemplateFile('noauth/extensions.py.txt', 'extensions.py')
        app_template = TemplateFile('noauth/app.py.txt', 'app.py')
        requirements_template = TemplateFile('noauth/requirements.txt.txt', 'requirements.txt')
        config_template = TemplateFile('noauth/config.py.txt', 'config.py')
        readme_template = TemplateFile('noauth/README.md.txt', 'README.md')
        db_models_blueprint = TemplateFile('noauth/db_models_blueprint.py.txt', 'db_models_blueprint.py')
        class Basic:
            flask_blueprint = TemplateFile('noauth/basic/flask_blueprint.py.txt', '${name}_blueprint.py')
            service_template = TemplateFile('noauth/basic/service_template.py.txt', '${name}_service.py')
        class FullCrud:
            flask_blueprint = TemplateFile('noauth/fullcrud/flask_blueprint.py.txt', '${name}_blueprint.py')
            service_template = TemplateFile('noauth/fullcrud/service_template.py.txt', '${name}_service.py')

    # flask_blueprint = TemplateFile('flask_blueprint.py.txt', '${name}_blueprint.py')
    # service_template = TemplateFile('service_template.py.txt', '${name}_service.py')
    # extensions_template = TemplateFile('extensions.py.txt', 'extensions.py')
    # app_template = TemplateFile('app.py.txt', 'app.py')
    # requirements_template = TemplateFile('requirements.txt.txt', 'requirements.txt')
    # config_template = TemplateFile('config.py.txt', 'config.py')
    # readme_template = TemplateFile('README.md.txt', 'README.md')
    # db_models_blueprint = TemplateFile('db_models_blueprint.py.txt', 'db_models_blueprint.py')

