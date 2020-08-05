from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, FloatField, SubmitField, SelectField, SelectMultipleField, DateField
from wtforms.validators import NumberRange, DataRequired, InputRequired

class SearchForm(FlaskForm):
	sfirstname = StringField("First Name")
	slastname = StringField("Last Name")
	search = SubmitField("Search")

class EmployeeForm(FlaskForm):
	dept_list = [("",""),]
	title_list = [("",""),]
	employeeid = IntegerField("ID", default="")
	gender = SelectField("Gender", choices=[("m", "m"), ("f", "f")])
	firstname = StringField("First Name", default="")
	lastname = StringField("Last Name", default="")
	department = SelectField("Deparment",choices=dept_list)
	title = SelectField("Title", choices=title_list)
	manager = StringField("Manager", default="")
	managerid = StringField("Manager ID", default="")
	add = SubmitField("Add")
	update = SubmitField("Update")
	delete = SubmitField("Delete")

class PayrollCtrlForm(FlaskForm):
	new_pyrl = SubmitField("New Payroll")
	list_pyrl = SelectMultipleField("All Payrolls", choices=[("",""),])
	open_pyrl = SubmitField("Open Payroll")
	delete_pyrl = SubmitField("Delete Payroll")

class PayrollDataForm(FlaskForm): 
	employeeid = IntegerField("ID")
	fullname = StringField("Full Name")
	basesalary = FloatField("Base Salary", validators=[NumberRange(min=0, message="Must be a number!"),])
	overtime = FloatField("Over Time", validators=[NumberRange(min=0, message="Must be a number!"),])
	allowance = FloatField("Allowance", validators=[NumberRange(min=0, message="Must be a number!"),])
	prjbonus = FloatField("Project Bonus", validators=[NumberRange(min=0, message="Must be a number!"),])
	advance = FloatField("Advance", validators=[NumberRange(min=0, message="Must be a number!"),])
	ul = FloatField("Unpaid Leave", validators=[NumberRange(min=0, message="Must be a number!"),])
	update_pyrl = SubmitField("Update Row")
	update_id = SubmitField("Update New ID")
	download = SubmitField("Download")
