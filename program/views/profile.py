from flask import url_for, render_template, session, request, redirect
from functools import wraps
from .. import app
from .. import db


account_type = {
	"ma" : "manager",
	"em" : "employee",
	"hr" : "hr"}

def require_access(access_level):
	def decorator(func):
		@wraps(func)
		def decorated_func(*args, **kwargs):
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

# Employee's profile page
@app.route("/user/<username>/<accounttype>/profile", methods=["GET", "POST"])
@require_login
def profile(username, accounttype):
	session["update_form"] = False
	msg = ""
	if request.method == "POST":
		session["update_form"] = request.form["edit"]
	profile = db.get_profile(session["employeeID"])
	home_user = "{}-home.html".format(accounttype)
	return render_template("profile.html", profile=profile, home_user=home_user, msg=msg)


@app.route("/user/<username>/<accounttype>/profile/update", methods=["GET", "POST"])
@require_login
def profile_update(username, accounttype):
	msg = ""
	if request.method == "POST":
		update_data = request.form.to_dict()
		res, msg = db.update_profile(list(update_data.values()))
	profile = db.get_profile(session["employeeID"])

	home_user = "{}-home.html".format(accounttype)
	return render_template("profile.html", profile=profile, home_user=home_user, msg=msg)