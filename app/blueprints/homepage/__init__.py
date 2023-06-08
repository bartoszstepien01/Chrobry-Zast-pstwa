from flask import Blueprint, render_template, redirect, url_for, request

homepage = Blueprint("homepage", __name__, template_folder="templates", static_folder="static")

@homepage.route("/")
def index():
	return render_template("index.html")