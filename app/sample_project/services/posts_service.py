from extensions import db
from models import Posts

def get_all():
    return db.session.query(Posts).all()

def get_one(id: int):
    return db.session.query(Posts).filter(Posts.id == id).first()

def add(payload: dict):
    rec = Posts(
        id= payload.get('id', None),
        user_id= payload.get('user_id', None),
        title= payload.get('title', None),
        content= payload.get('content', None),
        published_at= payload.get('published_at', None)
    )

    db.session.add(rec)
    db.session.commit()
    return rec

def update(id: int, payload):
    rec = get_one(id)

    if 'user_id' in payload:
        rec.user_id = payload.get('user_id')
    if 'title' in payload:
        rec.title = payload.get('title')
    if 'content' in payload:
        rec.content = payload.get('content')
    if 'published_at' in payload:
        rec.published_at = payload.get('published_at')

    db.session.commit()
    return rec


def delete(id: int):
    rec = get_one(id)
    db.session.delete(rec)
    db.session.commit()
    return {'status', 'ok'}