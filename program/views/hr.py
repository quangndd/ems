from flask import url_for, render_template, session, request, redirect, send_file
from functools import wraps
from .. import app
from .. import db
from .. import nav
from ..forms import *


account_type = {
	"ma" : "manager",
	"em" : "employee",
	"hr" : "hr"}

def require_access(access_level):
	def decorator(func):
		@wraps(func)
		def decorated_func(*args, **kwargs):
			if account_type[session["accounttype"]] == access_level:	# Check if account has access right
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

 # For HR
@app.route("/<username>/hr")
@require_access(access_level="hr")
def hr_home(username):
	# Create navigaton bar
	args={"username" : session["username"], "accounttype" : session["accounttype"]}
	nav.Bar("top", [
		nav.Item(label="Home", endpoint="hr_home", args=args),
		nav.Item(label="Profile", endpoint="profile", args=args),
		nav.Item(label="Employee", endpoint="manage_employee", args=args),
		nav.Item(label="Payroll", endpoint="manage_payroll", args=args),
		nav.Item(label="Logout", endpoint="logout")])
	return render_template("hr-home.html")


@app.route("/<username>/hr/man-em", methods=["GET", "POST"])
@require_access(access_level="hr")
def manage_employee(username):
	form_search = SearchForm()
	form_data = EmployeeForm()
	form_data.department.choices = db.get_deptname_list()
	form_data.title.choices = db.get_title_list()
	employees = None
	msg = ""
	#Search employee
	if form_search.search.data:
		employees = db.search_employees(form_search.sfirstname.data, form_search.slastname.data)
	#Add employee
	elif form_data.add.data:
		if not (form_data.firstname.data or form_data.lastname.data): 
			msg = "First Name and Last Name cannot be empty."
		elif form_data.employeeid.data:
			msg = "Duplicate ID, please clear fields first."
		else:
			res, msg = db.add_employee(form_data.gender.data, form_data.firstname.data, form_data.lastname.data, \
									   form_data.department.data, form_data.title.data, form_data.managerid.data)
			employees = db.search_employees(form_data.firstname.data, form_data.lastname.data)
	#Update employee
	elif form_data.update.data:
		if not (form_data.firstname.data or form_data.lastname.data): 
			msg = "First Name and Last Name can't be empty."
		elif not form_data.employeeid.data:
			msg = "ID cannot be empty, please select one to update."
		else:
			res, msg = db.update_employee(form_data.gender.data, form_data.firstname.data, form_data.lastname.data, form_data.department.data, \
									  	  form_data.title.data, form_data.managerid.data, form_data.employeeid.data)
		employees = db.search_employees(form_search.sfirstname.data, form_search.slastname.data)
	#Delete employee
	elif form_data.delete.data and form_data.employeeid.data:
		resutl, msg = db.delete_employee(form_data.employeeid.data)
		employees = db.search_employees(form_search.sfirstname.data, form_search.slastname.data)
	else:
		pass
	return render_template("hr-manage-employee.html",form_search=form_search, employees=employees, form_data=form_data, msg=msg)


@app.route("/<username>/hr/man-pyrl", methods=["GET", "POST"])
@require_access(access_level="hr")
def manage_payroll(username):
	pyrl_ctrl = PayrollCtrlForm()
	pyrls = db.get_existing_payrolls()
	if pyrls:
		for p in pyrls:
			pyrl_id_str = str(p["PayrollID"])[:4] + "/" + str(p["PayrollID"])[4:]
			pyrl_ctrl.list_pyrl.choices.append((pyrl_id_str, pyrl_id_str))
	else:
		pass
	# Check if new payroll button is hit.
	if pyrl_ctrl.new_pyrl.data:		
		pass
	# Check if open payroll button is hit
	elif pyrl_ctrl.open_pyrl.data and pyrl_ctrl.list_pyrl.data:		
		session["pyrl_id_str"] = pyrl_ctrl.list_pyrl.data[0]
		pyrl_id = int(session["pyrl_id_str"].replace("/", ""))
		session["pyrl_id"] = pyrl_id
		return redirect(url_for("open_selected_payroll", username=session["username"], pyrl_id=pyrl_id))
	# Check if delete payroll button is hit	
	elif pyrl_ctrl.delete_pyrl.data and pyrl_ctrl.list_pyrl.data:		 
		pyrl_id_str = pyrl_ctrl.list_pyrl.data[0]
		pyrl_id = int(pyrl_id_str.replace("/", ""))
		return redirect(url_for("delete_payroll", username=session["username"], pyrl_id=pyrl_id))
	else:
		pass
	return render_template("hr-manage-payroll.html", pyrl_ctrl=pyrl_ctrl, pyrls=pyrls)


@app.route("/<username>/hr/man-pyrl/new", methods=["GET", "POST"])
@require_access(access_level="hr")
def new_payroll(username):
	pyrl_ctrl = PayrollCtrlForm()
	pyrl_ctrl.new_pyrl.data = True
	if request.method == "POST":
		new_period = request.form["period"]
		new_pyrl_id = new_period.replace("-", "")
		res, msg = db.create_new_payroll(new_pyrl_id)
	pyrls = db.get_existing_payrolls()
	if pyrls:
		for p in pyrls:
			pyrl_id_str = str(p["PayrollID"])[:4] + "/" + str(p["PayrollID"])[4:]
			pyrl_ctrl.list_pyrl.choices.append((pyrl_id_str, pyrl_id_str))
	else:
		pass
	return render_template("hr-manage-payroll.html", pyrl_ctrl=pyrl_ctrl, pyrls=pyrls)


@app.route("/<username>/hr/man-pyrl/delete-<int:pyrl_id>", methods=["GET", "POST"])
@require_access(access_level="hr")
def delete_payroll(username, pyrl_id):
	pyrl_ctrl = PayrollCtrlForm()
	res, msg = db.delete_employee_payroll(pyrl_id)
	pyrls = db.get_existing_payrolls()
	if pyrls:
		for p in pyrls:
			pyrl_id_str = str(p["PayrollID"])[:4] + "/" + str(p["PayrollID"])[4:]
			pyrl_ctrl.list_pyrl.choices.append((pyrl_id_str, pyrl_id_str))
	else:
		pass
	return render_template("hr-manage-payroll.html", pyrl_ctrl=pyrl_ctrl, pyrls=pyrls)


@app.route("/<username>/hr/man-pyrl/open-pyrl-<int:pyrl_id>", methods=["GET", "POST"])
@require_access(access_level="hr")
def open_selected_payroll(username, pyrl_id):
	form_data = PayrollDataForm()
	error = ""


	# Check if update row button is hit
	if form_data.update_pyrl.data:
		if form_data.validate_on_submit() and form_data.employeeid.data:
			res, msg = db.update_payroll(pyrl_id, form_data.basesalary.data, form_data.overtime.data, form_data.allowance.data, \
										 form_data.prjbonus.data, form_data.advance.data, form_data.ul.data, form_data.employeeid.data)
			error = ""
		else:
			error = "Check all inputs again!"
	# Check if update id button is hit
	elif form_data.update_id.data:
		upd_id_res, upd_id_msg = db.update_payroll_IDs(pyrl_id)
	elif form_data.download.data:
		fpath = db.download_employee_payroll(pyrl_id)
		return send_file('.'+fpath, as_attachment=True)
	else:
		pass
	epyrls = db.get_employee_payroll(pyrl_id)
	return render_template("hr-current-payroll.html", form_data=form_data, epyrls=epyrls, pyrl_id=pyrl_id, error=error)