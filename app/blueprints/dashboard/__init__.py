from flask import Blueprint, render_template, redirect, url_for, request
from requests import get, patch
from os import getenv
from .auth import requires_auth
from ..bot import messenger_bot
from ...database import db
from ...database.models.User import User
from ...database.models.Setting import Setting

GRADES = []
CRONJOB_API_KEY = getenv("CRONJOB_API_KEY")
CRONJOB_JOB_ID = getenv("CRONJOB_JOB_ID")

dashboard = Blueprint("dashboard", __name__, template_folder="templates", static_folder="static")

@dashboard.route("/")
def index():
	return redirect(url_for("dashboard.users"))

@dashboard.route("/users")
@requires_auth
def users():
	users = User.query.all()
	return render_template("users.html", users=users)

@dashboard.route("/message", methods=["GET", "POST"])
@requires_auth
def message():
	GRADES = Setting.query.filter_by(name="grades").first().value.split(",")
	if request.method == "GET":
		return render_template("message.html", grades=GRADES)
	else:
		grades = request.form.getlist("grade")
		message = request.form.get("message")
		if not grades or not message: return render_template("message.html", grades=GRADES)

		users = User.query.filter(User.grade.in_(grades)).all()
		for user in users:
			messenger_bot.send_text_message(user.id, message)

		return render_template("message.html", grades=GRADES)

@dashboard.route("/data", methods=["GET", "POST"])
@requires_auth
def data():
	if request.method == "GET":
		substitutions_url = Setting.query.filter_by(name="substitutions_url").first().value
		dates_url = Setting.query.filter_by(name="dates_url").first().value
		metadata_url = Setting.query.filter_by(name="metadata_url").first().value
		grades = Setting.query.filter_by(name="grades").first().value.split(",")
		hours = Setting.query.filter_by(name="hours").first().value.split(",")
		return render_template("data.html", substitutions_url=substitutions_url, dates_url=dates_url, metadata_url=metadata_url, grades=grades, hours=hours)
	else:
		substitutions_url = request.form.get("substitutions_url")
		dates_url = request.form.get("dates_url")
		metadata_url = request.form.get("metadata_url")
		grades = request.form.get("grades")
		hours = request.form.get("hours")

		if not all(substitutions_url, dates_url, metadata_url, grades, hours): return render_template("data.html", substitutions_url=substitutions_url, dates_url=dates_url, metadata_url=metadata_url, grades=grades.split(","), hours=hours.split(","))

		Setting.query.filter_by(name="substitutions_url").first().value = substitutions_url
		Setting.query.filter_by(name="dates_url").first().value = dates_url
		Setting.query.filter_by(name="metadata_url").first().value = metadata_url
		Setting.query.filter_by(name="grades").first().value = grades
		Setting.query.filter_by(name="hours").first().value = hours

		db.session.commit()

		return render_template("data.html", substitutions_url=substitutions_url, dates_url=dates_url, metadata_url=metadata_url, grades=grades.split(","), hours=hours.split(","))

@dashboard.route("/cron", methods=["GET", "POST"])
@requires_auth
def cron():
	if request.method == "GET":
		response = get("https://api.cron-job.org/jobs/" + CRONJOB_JOB_ID, headers={ "Authorization": "Bearer " + CRONJOB_API_KEY })
		job_data = response.json()
		return render_template("cron.html", enabled=job_data["jobDetails"]["enabled"], interval=job_data["jobDetails"]["schedule"]["minutes"][1])
	
	enabled = request.form.get("enabled") is not None
	interval = int(request.form.get("interval"))
	patch("https://api.cron-job.org/jobs/" + CRONJOB_JOB_ID, headers={ "Authorization": "Bearer " + CRONJOB_API_KEY }, json={"job":{"enabled": enabled, "schedule": {"minutes": [i for i in range(0, 60, interval)]}}})
	return render_template("cron.html", enabled=enabled, interval=interval)

@dashboard.route("/stats")
@requires_auth
def stats():
    return render_template("stats.html")

@dashboard.route("/delete_user")
def delete_user():
	id = request.args.get("id")
	if not id: return redirect(url_for("dashboard.users"))

	user = User.query.filter_by(id=id).first()
	if not user: return redirect(url_for("dashboard.users"))

	db.session.delete(user)
	db.session.commit()
	messenger_bot.send_text_message(id, "Od teraz nie będziesz już otrzymywać powiadomień. Aby włączyć je ponownie, wpisz nazwę swojej klasy.")

	return redirect(url_for("dashboard.users"))