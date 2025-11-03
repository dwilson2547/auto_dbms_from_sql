from extensions import db
from models import Connections

def get_all():
    return db.session.query(Connections).all()