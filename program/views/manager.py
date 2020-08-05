from flask import url_for, render_template, session, request
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

# For Manager
@app.route("/user/<username>/ma")
@require_access(access_level="manager")
def manager_home(username):
	return render_template("ma-home.html")