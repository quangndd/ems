from flask import Flask, session, render_template
from flask import request, redirect, url_for
from flask_navigation import Navigation
from functools import wraps
from .forms import *
from .database import Database

app = Flask(__name__, instance_relative_config=True)
app.config.from_object("config.default")
app.config.from_pyfile("config.py", silent=True)
#app.config.from_envvar("APP_CONFIG_FILE")

db = Database(app)


nav = Navigation()
nav.init_app(app)


# @app.errorhandler(404)
# def page_not_found(err):
# 	return "Page is not found!", 404

# @app.errorhandler(401)
# def unauthorized(err):
# 	return "You are not allowed, please login!", 401

# @app.errorhandler(500)
# def internal_server_error(err):
# 	return "Somthing is wrong, please go back!", 500


from .views import profile
from .views import employee
from .views import hr
from .views import manager


account_type = {
	"ma" : "manager",
	"em" : "employee",
	"hr" : "hr"}

def require_access(access_level):
	def decorator(func):
		@wraps(func)
		def decorated_func(*args, **kwargs):
			with open("info.txt", "w") as f:
				f.write(f"{session['username']}, {session['accounttype']}")
			if account_type[session["accounttype"]] == access_level:
				return func(*args, **kwargs)
			else:
				return "You are not allowed!"
			return func
		return decorated_func
	return decorator


def require_login(func):
	@wraps(func)
	def decorated_func(*args, **kwargs):
		if session["username"]:
			pass
		else:
			return "You are in wrong place!"
		return func(*args, **kwargs)
	return decorated_func	


# Index page redirects to login page
@app.route("/")
def index():
	return redirect(url_for("login"))

# Login page
@app.route("/login", methods=["GET", "POST"])
def login():
	if request.method == "POST":
		username = request.form["username"]
		password = request.form["password"]
		account = db.get_existing_account(username, password)
		if account:
			session["username"] = account["Username"]
			session["accounttype"] = account["Type"]
			session["employeeID"] = account["EmployeeID"]
			user = account_type[session["accounttype"]]
			return redirect(url_for(f"{user}_home", username=session["username"], accounttype=session["accounttype"]))
		else:
			msg = "Incorrect credentials!"
			return render_template("login.html", msg=msg)
	else:
		return render_template("login.html")

# Log out
@require_login
@app.route("/logout")
def logout():
	session.clear()
	return redirect(url_for("login"))
