from extensions import db
from models import Users

def get_all():
    return db.session.query(Users).all()