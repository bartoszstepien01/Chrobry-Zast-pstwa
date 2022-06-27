from flask import Flask
import os
from blueprints import bot

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

app.register_blueprint(bot, url_prefix="/bot")