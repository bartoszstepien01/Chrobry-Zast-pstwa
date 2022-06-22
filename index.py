from flask import Flask, request

from flask_sqlalchemy import SQLAlchemy

from substitutions.substitutions import Substitutions
from substitutions.substitutionsdates import SubstitutionsDates
from substitutions.substitutionsparser import SubstitutionsParser

from pymessenger.bot import Bot

import os
import copy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DATABASE_URL")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN")

bot = Bot(ACCESS_TOKEN)

GRADES = os.getenv("GRADES").split(",")

substitutions = Substitutions()
dates = SubstitutionsDates()
parser = SubstitutionsParser()

parser.update_metadata()

class User(db.Model):
    id = db.Column(db.String(100), primary_key=True)
    grade = db.Column(db.String(5))

class Date(db.Model):
    date = db.Column(db.Date)
    current_substitutions = db.Column(db.JSON)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "GET":
        token_sent = request.args.get("hub.verify_token")
        if token_sent == VERIFY_TOKEN:
            return request.args.get("hub.challenge")
        else:
            return "Invalid verification token"
    else:
        output = request.get_json()
        for event in output["entry"]:
            messaging = event["messaging"]
            for message in messaging:
                if message.get("message"):
                    recipient_id = message["sender"]["id"]
                    text = message["message"].get("text").lower()

                    user = User.query.filter_by(id=recipient_id).first()

                    if text in GRADES:
                        if user:
                            user.grade = text
                            bot.send_text_message(recipient_id, "Od teraz będziesz otrzymywać powiadomienia dla klasy {0} 😀. Możesz je wyłączyć wpisując frazę STOP.".format(text))
                        else:
                            user = User(id=recipient_id, grade=text)
                            bot.send_text_message(recipient_id, "Od teraz będziesz otrzymywać powiadomienia za każdym razem, gdy pojawią się nowe zastępstwa dla klasy {0} 😀. Możesz je wyłączyć wpisując frazę STOP.".format(text))
                            
                        db.session.add(user)
                        db.session.commit()
                    elif text == "stop" and user:
                        db.session.delete(user)
                        db.session.commit()
                        bot.send_text_message(recipient_id, "Od teraz nie będziesz już otrzymywać powiadomień. Aby włączyć je ponownie, wpisz nazwę swojej klasy.")
                    else:
                        bot.send_text_message(recipient_id, "Przykro mi, ale nie istnieje klasa o podanej nazwie 😢")
                elif message.get("postback"):
                    recipient_id = message["sender"]["id"]
                    bot.send_text_message(recipient_id, "👋 Witaj!\nAby zacząć otrzymywać powiadomienia, wpisz nazwę swojej klasy")

          
    return "Message Processed"

@app.route("/check")
def check():
    date = dates.download_dates()[0]

    last_date = Date.query.first()

    if date < last_date.date: return "Nihil novi"

    temp = substitutions.get_substitutions(date)
    subs = {}

    for grade in GRADES:
        subs[grade] = substitutions.get_substitutions_for_grade(date, grade, temp)
        subs[grade] = parser.get_full_string(subs[grade], date)
    
    users = User.query.all()
    for user in users:
        bot.send_text_message(user.id, subs[user.grade])

    last_date.date = date
    temp2 = copy.deepcopy(temp)
    for key in temp2:
        for i, sub in enumerate(temp2[key]):
            temp2[key][i] = sub.__dict__
    
    last_date.current_substitutions = temp2

    db.session.add(last_date)
    db.session.commit()
    
    return "Success"