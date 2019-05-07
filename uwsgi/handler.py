import re
import sys
import logging
import subprocess
import requests
from datetime import datetime

from sqlalchemy.engine import create_engine
from init_db import table
from config import CONFIG


def application(env, start_response):
    try:
        uri = env.get('REQUEST_URI', '').split('/')
        _id = uri[2]
        engine = create_engine('mysql+mysqldb://{}:{}@{}:{}/{}'.format(
            CONFIG['DB_USER'], CONFIG['DB_PASS'], CONFIG['DB_HOST'], CONFIG['DB_PORT'], CONFIG['DB_NAME']))

        connection = engine.connect()
        result = connection.execute('SELECT * FROM credentials WHERE id={}'.format(int(_id),))
        result = next(iter(result), None)
        if result:
            r = requests.post(
                'https://secure.egamingonline.com/login.html',
                data={'username': result['login'], 'password': result['password']},
                headers={'Content-Type': 'application/x-www-form-urlencoded'},
                allow_redirects=False)
            string = r.headers.get('Set-Cookie', '')
            cookie = next(iter(re.findall(r'master_login=([\w\d]+);', string)), '')
            if cookie:
                exp = table.update().where(table.c.id ==_id).values(cookie_content=cookie, last_updated=datetime.now())
                connection.execute(exp)
                return [cookie.encode('utf-8')]
    except Exception as e:
        return [str(e).encode('utf-8')]
