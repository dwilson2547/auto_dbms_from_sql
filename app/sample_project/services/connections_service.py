from extensions import db
from models import Connections

def get_all():
    return db.session.query(Connections).all()

def get_one(user_id: int, friend_id: int):
    return db.session.query(Connections).filter(Connections.user_id == user_id & Connections.friend_id == friend_id).first()

def add(payload: dict):
    rec = Connections(
        user_id= payload.get('user_id', None),
        friend_id= payload.get('friend_id', None),
        connected_at= payload.get('connected_at', None)
    )

    db.session.add(rec)
    db.session.commit()
    return rec

def update(user_id: int, friend_id: int, payload):
    rec = get_one(user_id, friend_id)

    if 'connected_at' in payload:
        rec.connected_at = payload.get('connected_at')

    db.session.commit()
    return rec


def delete(user_id: int, friend_id: int):
    rec = get_one(user_id, friend_id)
    db.session.delete(rec)
    db.session.commit()
    return {'status', 'ok'}