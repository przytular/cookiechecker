import re
import sys
import logging
import subprocess
import requests
from bs4 import BeautifulSoup as BS
from datetime import datetime

from sqlalchemy.engine import create_engine
from init_db import table
from config import CONFIG


def application(env, start_response):
    start_response('200 OK', [('Content-Type','text/html')])
    uri = env.get('REQUEST_URI', '').split('/')
    _id = uri[2]
    engine = create_engine('mysql+mysqldb://{}:{}@{}:{}/{}'.format(
        CONFIG['DB_USER'], CONFIG['DB_PASS'], CONFIG['DB_HOST'], CONFIG['DB_PORT'], CONFIG['DB_NAME']))

    connection = engine.connect()
    result = connection.execute('SELECT * FROM credentials WHERE id={}'.format(int(_id),))
    result = next(iter(result), None)
    if result:
        if result['ASPNET']:
            r = requests.get(result['url'], cookies={result['cookie_name']: result['cookie_content']})
            if r.history:
                r = requests.get(result['url'])
                r2 = requests.post(
                    'https://aff.gowildpartners.com/affiliates/Account/Login',
                    data={
                        'UserName': result['login'],
                        'Password': result['password'],
                        '__RequestVerificationToken': BS(r.text).find(
                            'input', {'name': '__RequestVerificationToken'})['value']},
                    cookies=r.cookies,
                    headers={'Content-Type': 'application/x-www-form-urlencoded'})
                soup = BS(r2.text)
                if soup.find(id='affName'):
                    exp = table.update().where(table.c.id ==_id).values(cookie_content=r.cookies['ASP.NET_SessionId'], last_updated=datetime.now())
                    connection.execute(exp)
                    return [r.cookies['ASP.NET_SessionId'].encode('utf-8')]
                else:
                    return [r2.text.encode('utf-8')]
            else:
                return [result['cookie_content'].encode('utf-8')]
        else:
            r = requests.post(
                result['url'],
                data={'username': result['login'], 'password': result['password']},
                headers={'Content-Type': 'application/x-www-form-urlencoded'},
                allow_redirects=False)
            string = r.headers.get('Set-Cookie', '')
            rex = re.compile('{}=([\w\d]+);'.format(result['cookie_name'],))
            cookie = next(iter(re.findall(rex, string)), '')
            if cookie:
                exp = table.update().where(table.c.id ==_id).values(cookie_content=cookie, last_updated=datetime.now())
                connection.execute(exp)
                return [cookie.encode('utf-8')]
            else:
                return [b'Couldn\'t log in. Probably wrong credentials?']
