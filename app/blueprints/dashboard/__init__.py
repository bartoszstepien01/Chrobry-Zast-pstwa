from flask import Blueprint, render_template, redirect, url_for
from .auth import requires_auth

dashboard = Blueprint("dashboard", __name__, template_folder="templates")

@dashboard.route("/")
def index():
	return redirect(url_for("dashboard.users"))

@dashboard.route("/users")
@requires_auth
def users():
	return render_template("users.html")

@dashboard.route("/message")
@requires_auth
def message():
    return render_template("message.html")

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