from flask import Blueprint, request, jsonify

from services.users_service import get_all, add, get_one, update, delete
from forms.users_form import Users_form

form = Users_form()

users_blueprint = Blueprint('users', __name__, url_prefix='/users')

@users_blueprint.route('/get_all', methods=['GET'])
def get_all_users():
    return jsonify(get_all())

@users_blueprint.route('/get/<int:id>', methods=['GET'])
def get_one_users(id: int):
    return jsonify(get_one(id))

@users_blueprint.route('/add', methods=['POST'])
def add_users():
    data = request.get_json()
    return jsonify(add(data))

@users_blueprint.route('/update/<int:id>', methods=['POST'])
def update_users(id: int):
    data = request.get_json()
    return jsonify(update(id, data))

@users_blueprint.route('/delete/id', methods=['DELETE'])
def delete_users(id: int):
    return jsonify(delete(id))

@users_blueprint.route('/form-data', methods=['GET'])
def get_form_users():
    return jsonify(form.get_form_data())