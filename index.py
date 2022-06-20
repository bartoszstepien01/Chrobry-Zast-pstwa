from flask import Flask, request

from substitutions.substitutions import Substitutions
from substitutions.substitutionsdates import SubstitutionsDates
from substitutions.substitutionsparser import SubstitutionsParser

from pymessenger.bot import Bot

import os

app = Flask(__name__)

ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN")

bot = Bot(ACCESS_TOKEN)

substitutions = Substitutions()
dates = SubstitutionsDates()
parser = SubstitutionsParser()

parser.update_metadata()


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
                    text = message["message"].get("text")

                    date = dates.download_dates()[0]
                    substitution = substitutions.get_substitutions_for_grade(date, text)

                    bot.send_text_message(recipient_id, parser.get_full_string(substitution, date))
          
    return "Message Processed"