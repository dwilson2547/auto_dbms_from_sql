from extensions import db
from models import Users

def get_all():
    return db.session.query(Users).all()

def get_one(id: int):
    return db.session.query(Users).filter(Users.id == id).first()

def add(payload: dict):
    rec = Users(
        id= payload.get('id', None),
        username= payload.get('username', None),
        email= payload.get('email', None),
        is_active= payload.get('is_active', None)
    )

    db.session.add(rec)
    db.session.commit()
    return rec

def update(id: int, payload):
    rec = get_one(id)

    if 'username' in payload:
        rec.username = payload.get('username')
    if 'email' in payload:
        rec.email = payload.get('email')
    if 'is_active' in payload:
        rec.is_active = payload.get('is_active')

    db.session.commit()
    return rec


def delete(id: int):
    rec = get_one(id)
    db.session.delete(rec)
    db.session.commit()
    return {'status', 'ok'}