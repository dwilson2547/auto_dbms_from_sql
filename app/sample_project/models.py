from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Users(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(50), nullable=False, unique=True)
    email = db.Column(db.String(100), nullable=False)
    is_active = db.Column(db.Boolean)


class Posts(db.Model):
    __tablename__ = 'posts'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, nullable=False)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text)
    published_at = db.Column(db.Date)


class Connections(db.Model):
    __tablename__ = 'connections'

    user_id = db.Column(db.Integer, primary_key=True)
    friend_id = db.Column(db.Integer, primary_key=True)
    connected_at = db.Column(db.Date)

