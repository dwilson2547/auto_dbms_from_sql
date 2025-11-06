import os
from urllib.parse import quote_plus

db_url = os.getenv('db_url')
db_user = os.getenv('db_user')
db_pass = os.getenv('db_pass')
db_name = os.getenv('db_name')
db_type = os.getenv('db_type', 'postgres').lower()

type_mapping = {
    'postgres': 'postgresql+psycopg2',
    'mysql': 'mysql+pymysql',
}

class Config:
    SQLALCHEMY_DATABASE_URI=type_mapping.get(db_type) + '://%s:%s@%s/%s' % (db_user.strip(), quote_plus(db_pass.strip()), db_url.strip(), db_name.strip())
