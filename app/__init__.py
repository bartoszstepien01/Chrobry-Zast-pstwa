from flask import Flask
from os import getenv

from .blueprints.homepage import homepage
from .blueprints.bot import bot
from .blueprints.dashboard import dashboard

from .database import db

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = getenv("DATABASE_URL")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db.init_app(app)

app.register_blueprint(homepage)
app.register_blueprint(bot, url_prefix="/bot")
app.register_blueprint(dashboard, url_prefix="/dashboard")