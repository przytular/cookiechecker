import re
import sys
import logging
import subprocess
import requests

from sqlalchemy.engine import create_engine
from config import CONFIG


def application(env, start_response):
    uri = env.get('REQUEST_URI', '').split('/')

    engine = create_engine('mysql+mysqldb://{}:{}@{}:{}/{}'.format(
        CONFIG['DB_USER'], CONFIG['DB_PASS'], CONFIG['DB_HOST'], CONFIG['DB_PORT'], CONFIG['DB_NAME']))

    connection = engine.connect()
    result = connection.execute('SELECT * FROM credentials WHERE id={}'.format(int(1),))
    result = next(iter(result), None)
    if result:
        r = requests.post(
            'https://secure.egamingonline.com/login.html',
            data={'username': result['login'], 'password': 'dupakupa01'},
            headers={'Content-Type': 'application/x-www-form-urlencoded'},
            allow_redirects=False)
        string = r.headers.get('Set-Cookie', '')
        cookie = next(iter(re.findall(r'master_login=([\w\d]+);', string)), '')
        return [cookie.encode('utf-8')]
    else:
        return [b'No account with that number found.']
