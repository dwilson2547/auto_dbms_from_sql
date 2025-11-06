from flask import Blueprint, request, jsonify

from services.posts_service import get_all, add, get_one, update, delete
from forms.posts_form import Posts_form

form = Posts_form()

posts_blueprint = Blueprint('posts', __name__, url_prefix='/posts')

@posts_blueprint.route('/get_all', methods=['GET'])
def get_all_posts():
    return jsonify(get_all())

@posts_blueprint.route('/get/<int:id>', methods=['GET'])
def get_one_posts(id: int):
    return jsonify(get_one(id))

@posts_blueprint.route('/add', methods=['POST'])
def add_posts():
    data = request.get_json()
    return jsonify(add(data))

@posts_blueprint.route('/update/<int:id>', methods=['POST'])
def update_posts(id: int):
    data = request.get_json()
    return jsonify(update(id, data))

@posts_blueprint.route('/delete/id', methods=['DELETE'])
def delete_posts(id: int):
    return jsonify(delete(id))

@posts_blueprint.route('/form-data', methods=['GET'])
def get_form_posts():
    return jsonify(form.get_form_data())