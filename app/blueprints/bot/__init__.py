from flask import Blueprint, request
from pymessenger.bot import Bot
from os import getenv
from copy import deepcopy

from .substitutions.substitutions import Substitutions
from .substitutions.substitutionsdates import SubstitutionsDates
from .substitutions.substitutionsparser import SubstitutionsParser
from ...database import db
from ...database.models.User import User
from ...database.models.Date import Date
from ...database.models.Setting import Setting

ACCESS_TOKEN = getenv("ACCESS_TOKEN")
VERIFY_TOKEN = getenv("VERIFY_TOKEN")
CHECK_TOKEN = getenv("CHECK_TOKEN")
GRADES = Setting.query.filter_by(name="grades").first().value.split(",")

bot = Blueprint("bot", __name__)
messenger_bot = Bot(ACCESS_TOKEN)

Substitutions.URL = Setting.query.filter_by(name="substitutions_url").first().value
SubstitutionsDates.DATES_URL = Setting.query.filter_by(name="dates_url").first().value
SubstitutionsParser.HOURS = Setting.query.filter_by(name="hours").first().value.split(",")
SubstitutionsParser.METADATA_URL = Setting.query.filter_by(name="metadata_url").first().value

substitutions = Substitutions()
dates = SubstitutionsDates()
parser = SubstitutionsParser()

parser.update_metadata()

@bot.route("/webhook", methods=["GET", "POST"])
def webhook():
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

					GRADES = Setting.query.filter_by(name="grades").first().value.split(",")

					if text in GRADES:
						if user:
							user.grade = text
							messenger_bot.send_text_message(recipient_id, "Od teraz będziesz otrzymywać powiadomienia dla klasy {0} 😀. Możesz je wyłączyć wpisując frazę STOP.".format(text))
						else:
							user = User(id=recipient_id, grade=text)
							messenger_bot.send_text_message(recipient_id, "Od teraz będziesz otrzymywać powiadomienia za każdym razem, gdy pojawią się nowe zastępstwa dla klasy {0} 😀. Możesz je wyłączyć wpisując frazę STOP.".format(text))
                            
						db.session.add(user)
						db.session.commit()
					elif text == "stop" and user:
						db.session.delete(user)
						db.session.commit()
						messenger_bot.send_text_message(recipient_id, "Od teraz nie będziesz już otrzymywać powiadomień. Aby włączyć je ponownie, wpisz nazwę swojej klasy.")
					else:
						messenger_bot.send_text_message(recipient_id, "Przykro mi, ale nie istnieje klasa o podanej nazwie 😢")
				elif message.get("postback"):
					recipient_id = message["sender"]["id"]
					messenger_bot.send_text_message(recipient_id, "👋 Witaj!\nAby zacząć otrzymywać powiadomienia, wpisz nazwę swojej klasy")
    
	return "Message Processed"

@bot.route("/check")
def check():
	if request.headers.get("Token") != CHECK_TOKEN: return "Invalid verification token"

	GRADES = Setting.query.filter_by(name="grades").first().value.split(",")
	Substitutions.URL = Setting.query.filter_by(name="substitutions_url").first().value
	SubstitutionsDates.DATES_URL = Setting.query.filter_by(name="dates_url").first().value
	SubstitutionsParser.HOURS = Setting.query.filter_by(name="hours").first().value.split(",")
	SubstitutionsParser.METADATA_URL = Setting.query.filter_by(name="metadata_url").first().value

	date = dates.download_dates()[0]
	temp = substitutions.get_substitutions(date)

	temp2 = deepcopy(temp)
	for key in temp2:
		for i, sub in enumerate(temp2[key]):
			temp2[key][i] = sub.__dict__

	last_date = Date.query.first()

	if last_date.date == date and last_date.current_substitutions == temp2: return "Nihil novi"

	update = date == last_date.date
	subs = {}

	for grade in GRADES:
		subs[grade] = substitutions.get_substitutions_for_grade(date, grade, temp)
		subs[grade] = parser.get_full_string(subs[grade], date)
		if update: subs[grade] = subs[grade].replace("Zastępstwa", "Aktualizacja zastępstw")
    
	users = User.query.all()
	for user in users:
		messenger_bot.send_text_message(user.id, subs[user.grade])

	last_date.date = date
	last_date.current_substitutions = temp2

	db.session.add(last_date)
	db.session.commit()
    
	return "Success"