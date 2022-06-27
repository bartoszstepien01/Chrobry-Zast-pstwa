from flask import Blueprint, render_template, redirect, url_for, request
from os import getenv
from .auth import requires_auth
from ..bot import messenger_bot
from ...database import db
from ...database.models.User import User

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
	if request.method == 'GET':
		return render_template("message.html", grades=getenv("GRADES").split(","))
	else:
		grades = request.form.getlist("grade")
		message = request.form.get("message")
		if not grades or not message: return render_template("message.html", grades=getenv("GRADES").split(","))

		users = User.query.filter_by(User.grade.in_(grades)).all()
		for user in users:
			messenger_bot.send_text_message(user.id, message)

		return render_template("message.html", grades=getenv("GRADES").split(","))

@dashboard.route("/data")
@requires_auth
def data():
    return render_template("data.html")

@dashboard.route("/cron")
@requires_auth
def cron():
    return render_template("cron.html")

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