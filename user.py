from models import *

import hashlib

def _sha256(password):
    m = hashlib.sha256()
    m.update(bytes(password,'utf8'))
    m.update(b"lingge2017")
    return m.hexdigest()

def login(username, password):
    password=_sha256(password)

    try:
        c=User.select().where(User.username==username,User.password==password).get()
        return c
    except Exception as ex:

        return None






def create(username, password):
    U, created = User.get_or_create(
        username=username,
        defaults={'password': _sha256(password)})

    return U.id, created
