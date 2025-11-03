from string import Template
import os

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
            return file.read()
    
    def gen_name(self, name: str) -> str:
        """Generate the output filename by substituting variables from context."""
        template = Template(self.name_template)
        return template.substitute({'name': name})
    
    def write(self, output_dir: str, name: str, context: dict):
        """Write the template content to the specified output path, substituting variables from context."""
        template = Template(self.content)
        rendered_content = template.substitute(context)

        with open(os.path.join(output_dir, self.gen_name(name)), 'w') as file:
            file.write(rendered_content)

class Templates:
    flask_blueprint = TemplateFile('flask_blueprint.py.txt', '${name}_blueprint.py')
    form_template = TemplateFile('form_blueprint.py.txt', '${name}_form.py')
    service_template = TemplateFile('service_template.py.txt', '${name}_service.py')
    extensions_template = TemplateFile('extensions.py.txt', 'extensions.py')
    app_template = TemplateFile('app.py.txt', 'app.py')
    requirements_template = TemplateFile('requirements.txt.txt', 'requirements.txt')
    config_template = TemplateFile('config.py.txt', 'config.py')
    readme_template = TemplateFile('README.md.txt', 'README.md')

