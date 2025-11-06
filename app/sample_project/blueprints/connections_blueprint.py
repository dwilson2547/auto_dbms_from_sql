from flask import Blueprint, request, jsonify

from services.connections_service import get_all, add, get_one, update, delete
from forms.connections_form import Connections_form

form = Connections_form()

connections_blueprint = Blueprint('connections', __name__, url_prefix='/connections')

@connections_blueprint.route('/get_all', methods=['GET'])
def get_all_connections():
    return jsonify(get_all())

@connections_blueprint.route('/get/<int:user_id>/<int:friend_id>', methods=['GET'])
def get_one_connections(user_id: int, friend_id: int):
    return jsonify(get_one(user_id, friend_id))

@connections_blueprint.route('/add', methods=['POST'])
def add_connections():
    data = request.get_json()
    return jsonify(add(data))

@connections_blueprint.route('/update/<int:user_id>/<int:friend_id>', methods=['POST'])
def update_connections(user_id: int, friend_id: int):
    data = request.get_json()
    return jsonify(update(user_id, friend_id, data))

@connections_blueprint.route('/delete/user_id, friend_id', methods=['DELETE'])
def delete_connections(user_id: int, friend_id: int):
    return jsonify(delete(user_id, friend_id))

@connections_blueprint.route('/form-data', methods=['GET'])
def get_form_connections():
    return jsonify(form.get_form_data())