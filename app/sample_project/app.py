from flask import Flask
from extensions import db
import cherrypy

from blueprints.users_blueprint import users_blueprint
from blueprints.posts_blueprint import posts_blueprint
from blueprints.connections_blueprint import connections_blueprint


def create_app():
    app = Flask(__name__)

    app.config.from_object('config.Config')

    db.init_app(app)

    app.register_blueprint(users_blueprint, url_prefix='/api')   # Blueprint name is added to url in blueprint file
    app.register_blueprint(posts_blueprint, url_prefix='/api')   # Blueprint name is added to url in blueprint file
    app.register_blueprint(connections_blueprint, url_prefix='/api')   # Blueprint name is added to url in blueprint file


    with app.app_context():
        db.create_all()
    
    return app

def init_server():
    app = create_app()
    cherrypy.tree.graft(app, '/')
    cherrypy.config.update({
        'server.socker_host': '0.0.0.0',
        'server.socket_port': 8080,
        'engine.autoreload.on': False
    })

if __name__ == '__main__':
    init_server()
    cherrypy.engine.start()
