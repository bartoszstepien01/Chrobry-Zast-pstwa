from flask_sqlalchemy import SQLAlchemy

from ..index import app

db = SQLAlchemy(app)