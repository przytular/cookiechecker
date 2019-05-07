from sqlalchemy import schema, types, text
from sqlalchemy.engine import create_engine
from config import CONFIG

metadata = schema.MetaData()

table = schema.Table('credentials', metadata,
    schema.Column('id', types.Integer, primary_key=True),
    schema.Column('login', types.Unicode(255), default=u''),
    schema.Column('password', types.Unicode(255), default=u''),
    schema.Column('cookie_content', types.Unicode(255), default=u''),
    schema.Column('last_updated', types.DateTime, server_default=text('NOW()'))
)

### CONNECT TO DB
engine = create_engine('mysql+mysqldb://{}:{}@{}:{}/{}'.format(
	CONFIG['DB_USER'], CONFIG['DB_PASS'], CONFIG['DB_HOST'], CONFIG['DB_PORT'], CONFIG['DB_NAME']))
metadata.bind = engine

### CREATE TABLES
metadata.create_all(checkfirst=True)
