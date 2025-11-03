import os
import json

class Posts_form():

    filename = 'posts_formly.json'
    path = path = os.path.join(os.path.dirname(__file__), 'json', filename)
    form_data: dict

    def __init__(self):
        content = ''
        with open(self.path, 'r') as f:
            content = f.read()
        self.form_data = json.loads(content)

    def get_form_data(self):
        return self.form_data