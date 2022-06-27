# Big thanks to dirn (https://stackoverflow.com/users/978961/dirn) for sharing authentication code on StackOverflow
# https://stackoverflow.com/a/29725558

from flask import request, Response
from functools import wraps
from os import getenv

def check_auth(username, password):
    return username == getenv("DASHBOARD_USERNAME") and password == getenv("DASHBOARD_PASSWORD")

def authenticate():
    return Response("Incorrect username or password", 401, { "WWW-Authenticate": 'Basic realm="Login Required"' })

def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return authenticate()
        return f(*args, **kwargs)
    return decorated