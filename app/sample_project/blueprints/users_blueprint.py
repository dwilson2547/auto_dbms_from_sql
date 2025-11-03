from flask import Blueprint, current_app, request, jsonify

from services.users_service import get_all
from forms.users_form import Users_form

form = Users_form()

users_blueprint = Blueprint('users', __name__, url_prefix='/users')

users_blueprint.route('/get', methods=['GET'])
def get_all_users():
    return jsonify(get_all())

users_blueprint.route('/form-data', methods=['GET'])
def get_form_users():
    return jsonify(form.get_form_data())