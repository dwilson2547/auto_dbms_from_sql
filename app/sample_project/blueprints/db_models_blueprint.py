from flask import Blueprint, jsonify

db_models_blueprint = Blueprint('db_models', __name__)

@db_models_blueprint.route('/get_all', methods=['GET'])
def get_all():
    payload = [{'name': 'Users', 'path': '/users'}, {'name': 'Posts', 'path': '/posts'}, {'name': 'Connections', 'path': '/connections'}]
    return jsonify(payload)

