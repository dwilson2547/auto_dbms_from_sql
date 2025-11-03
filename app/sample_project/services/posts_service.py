from extensions import db
from models import Posts

def get_all():
    return db.session.query(Posts).all()