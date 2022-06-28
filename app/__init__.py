from flask import Flask
from os import getenv

from .blueprints.bot import bot
from .blueprints.dashboard import dashboard

from .database import db

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = getenv("DATABASE_URL")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)
with app.app_context():
	db.create_all()

app.register_blueprint(bot, url_prefix="/bot")
app.register_blueprint(dashboard, url_prefix="/dashboard")