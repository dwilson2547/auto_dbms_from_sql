from flask import Blueprint, current_app, request, jsonify

from services.posts_service import get_all
from forms.posts_form import Posts_form

form = Posts_form()

posts_blueprint = Blueprint('posts', __name__, url_prefix='/posts')

posts_blueprint.route('/get', methods=['GET'])
def get_all_posts():
    return jsonify(get_all())

posts_blueprint.route('/form-data', methods=['GET'])
def get_form_posts():
    return jsonify(form.get_form_data())