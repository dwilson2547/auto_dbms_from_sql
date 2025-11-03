from flask import Blueprint, current_app, request, jsonify

from services.connections_service import get_all
from forms.connections_form import Connections_form

form = Connections_form()

connections_blueprint = Blueprint('connections', __name__, url_prefix='/connections')

connections_blueprint.route('/get', methods=['GET'])
def get_all_connections():
    return jsonify(get_all())

connections_blueprint.route('/form-data', methods=['GET'])
def get_form_connections():
    return jsonify(form.get_form_data())