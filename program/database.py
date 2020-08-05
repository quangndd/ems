from flaskext.mysql import MySQL
from pymysql.cursors import DictCursor
import xlsxwriter
import os

class Database():
	def __init__(self, app):
		self.mysql = MySQL(cursorclass=DictCursor)
		self.mysql.init_app(app)


	def get_existing_account(self, username, password):
		curs = self.mysql.get_db().cursor()
		sql = "SELECT * FROM tbl_accounts WHERE Username='{0}' and Password='{1}';"\
				.format(username, password)
		curs.execute(sql)
		account = curs.fetchone()
		curs.close()
		return account


	def get_profile(self, employeeID):
		curs = self.mysql.get_db().cursor()
		sql = """SELECT 
			E.EmployeeID, E.Gender, E.FirstName, E.LastName, D.DeptName, T.TitleName, 
			CONCAT(E1.FirstName, ' ', E1.LastName) as ManagerName, E.ManagerID FROM tbl_employee E 
			LEFT JOIN tbl_dept D ON E.DeptID = D.DeptID 
			LEFT JOIN tbl_title T ON T.TitleID = E.TitleID 
			LEFT JOIN tbl_employee E1 ON E.ManagerID = E1.EmployeeID
			HAVING E.EmployeeID={0};""".format(employeeID)
		curs.execute(sql)
		profile = curs.fetchone()
		curs.close()
		return profile


	def update_profile(self, pf_data):
		try:
			curs = self.mysql.get_db().cursor()		
			sql = """UPDATE tbl_employee SET Gender = '{1}',  FirstName = '{2}',  LastName = '{3}' WHERE EmployeeID = {0};"""\
				.format(*pf_data)
			curs.execute(sql)
			self.mysql.get_db().commit()
			return True, "Done."
		except Exception as err:
			self.mysql.get_db().rollback()
			return False, err
		finally:
			curs.close()


	def search_employees(self, firstname, lastname):
		curs = self.mysql.get_db().cursor()
		if firstname and lastname:
			cond_str = "E.FirstName='{0}' AND E.LastName='{1}'".format(firstname.title(), lastname.title())
		elif firstname and not lastname:
			cond_str = "E.FirstName='{0}'".format(firstname.title())
		elif not firstname and lastname:
			cond_str = "E.LastName='{0}'".format(lastname.title())
		else:
			cond_str = "1"			

		sql = """SELECT 
			E.EmployeeID, E.Gender, E.FirstName, E.LastName, D.DeptName, T.TitleName, 
			CONCAT(E1.FirstName, ' ', E1.LastName) as ManagerName, E.ManagerID FROM tbl_employee E 
			LEFT JOIN tbl_dept D ON E.DeptID = D.DeptID 
			LEFT JOIN tbl_title T ON T.TitleID = E.TitleID 
			LEFT JOIN tbl_employee E1 ON E.ManagerID = E1.EmployeeID
			WHERE {0};""".format(cond_str)

			#HAVING E.FirstName='{0}' AND E.LastName='{1}';"""\
			#	.format(firstname, lastname)
		curs.execute(sql)
		employees = curs.fetchall()
		curs.close()
		return employees


	def add_employee(self, gender, firstname, lastname, department, title, managerid):
		try:
			curs = self.mysql.get_db().cursor()
			if not managerid:
				managerid = "NULL"
			sql = """INSERT INTO tbl_employee VALUES (NULL, '{}', '{}', '{}',(SELECT DeptID FROM tbl_dept WHERE DeptName='{}'), \
				(SELECT TitleID FROM tbl_title WHERE TitleName='{}'), {});""".format(gender, firstname, \
					lastname, department, title, managerid)
			curs.execute(sql)
			self.mysql.get_db().commit()
			return True, "Done."
		except Exception as err:
			self.mysql.get_db().rollback()
			return False, "Failed"
		finally:
			curs.close()


	def update_employee(self, gender, firstname, lastname, department, title, managerid, employeeid):
		try:
			curs = self.mysql.get_db().cursor()
			if not managerid:
				managerid = "NULL"
			sql = """UPDATE tbl_employee SET Gender = '{}',  FirstName = '{}',  LastName = '{}', \
				DeptID = (SELECT DeptID FROM tbl_dept WHERE DeptName = '{}'), TitleID = (SELECT TitleID FROM tbl_title WHERE TitleName = '{}'), \
				ManagerID = {} WHERE EmployeeID = {};""".format(gender, firstname, lastname, department, title, managerid, employeeid)
			curs.execute(sql)
			self.mysql.get_db().commit()
			return True, "Done."
		except Exception as err:
			self.mysql.get_db().rollback()
			return False, err
		finally:
			curs.close()


	def delete_employee(self, eid):
		try:
			curs = self.mysql.get_db().cursor()
			sql = """DELETE FROM tbl_employee WHERE EmployeeID={};"""\
					.format(eid)
			curs.execute(sql)
			self.mysql.get_db().commit()
			return True, "Done."
		except Exception as err:
			self.mysql.get_db().rollback()
			return False, err
		finally:
			curs.close()


	def get_deptname_list(self):
		curs = self.mysql.get_db().cursor()
		sql = "SELECT * FROM tbl_dept;"
		curs.execute(sql)
		depts=curs.fetchall()
		curs.close()
		deptname_list = [("",""),]
		for d in depts:
			deptname_list.append((d["DeptName"],d["DeptName"]))
		return deptname_list


	def get_title_list(self):
		curs = self.mysql.get_db().cursor()
		sql = "SELECT * FROM tbl_title;"
		curs.execute(sql)
		titles=curs.fetchall()
		curs.close()
		titlename_list = [("",""),]
		for t in titles:
			titlename_list.append((t["TitleName"],t["TitleName"]))
		return titlename_list


	def get_existing_payrolls(self):
		curs = self.mysql.get_db().cursor()
		sql = """SELECT * FROM tbl_payrolls;"""
		curs.execute(sql)
		payrolls = curs.fetchall()
		curs.close()
		return payrolls


	def get_employee_payroll(self, payroll_id):
		curs = self.mysql.get_db().cursor()
		total_amount_sql = "(P.BaseSalary + P.OverTime + P.Allowance + P.ProjectBonus - P.Advance - P.UnpaidLeave) AS Total"
		sql = """SELECT P.EmployeeID, CONCAT(E.FirstName, ' ', E.LastName) AS FullName, D.DeptName, T.TitleName, \
			P.BaseSalary, P.OverTime, P.Allowance, P.ProjectBonus, P.Advance, P.UnpaidLeave, {0} FROM payroll_{1} P
			LEFT JOIN tbl_employee E ON P.EmployeeID = E.EmployeeID
			LEFT JOIN tbl_dept D ON E.DeptID = D.DeptID
			LEFT JOIN tbl_title T ON E.TitleID = T.TitleID;""".format(total_amount_sql, payroll_id)
		curs.execute(sql)
		epayrolls = curs.fetchall()
		curs.close()
		return	epayrolls


	def update_payroll(self, pyrl_id, basesalary, overtime, allowance, prjbonus, advance, ul, employeeid):
		try:
			curs = self.mysql.get_db().cursor()
			sql = """UPDATE payroll_{0} SET BaseSalary = '{1}',  OverTime = '{2}',  Allowance = '{3}', ProjectBonus = '{4}', 
				Advance = '{5}', UnpaidLeave = '{6}' WHERE EmployeeID = '{7}';""".format(pyrl_id, basesalary, overtime, allowance, \
					prjbonus, advance, ul, employeeid)
			curs.execute(sql)
			self.mysql.get_db().commit()
			return True, "Done."
		except Exception as err:
			self.mysql.get_db().rollback()
			return False, err
		finally:
			curs.close()


	def create_payroll_tbl(self, payroll_id):
		try:
			curs = self.mysql.get_db().cursor()
			sql = """CREATE TABLE payroll_{0}(
				EmployeeID INT NOT NULL,
				BaseSalary FLOAT(3) DEFAULT 0,
				OverTime FLOAT(3) DEFAULT 0,
				Allowance FLOAT(3) DEFAULT 0,
				ProjectBonus FLOAT(3) DEFAULT 0,
				Advance FLOAT(3) DEFAULT 0,
				UnpaidLeave FLOAT(3) DEFAULT 0,
				FOREIGN KEY (EmployeeID)
					REFERENCES tbl_employee(EmployeeID)
					ON DELETE CASCADE
					ON UPDATE CASCADE,
				PRIMARY KEY (EmployeeID)) ENGINE=INNODB;""".format(payroll_id)
			curs.execute(sql)
			return True, "Done."
		except Exception as err:
			return False, err
		finally:
			curs.close()



	def insert_IDs_newpayroll(self, payroll_id):
		try:
			curs = self.mysql.get_db().cursor()
			sql = """INSERT INTO payroll_{0} (EmployeeID) (SELECT EmployeeID FROM tbl_employee);""".format(payroll_id)
			curs.execute(sql)
			self.mysql.get_db().commit()
			return True, "Done."
		except Exception as err:
			return False, err
		finally:
			curs.close()

	def add_to_payroll_list(self, payroll_id):
		try:
			curs = self.mysql.get_db().cursor()
			sql = "INSERT INTO tbl_payrolls VALUES({});".format(payroll_id)
			curs.execute(sql)
			self.mysql.get_db().commit()
			return True, "Done."
		except Exception as err:
			self.mysql.get_db().rollback()
			return False, err
		finally:
			curs.close()

	def create_new_payroll(self, payroll_id):
		try:
			curs = self.mysql.get_db().cursor()
			create_res, create_msg = self.create_payroll_tbl(payroll_id)	# Create new table
			insert_res, insert_msg = self.insert_IDs_newpayroll(payroll_id) # Create default table list
			if create_res and insert_res:
				res, msg = self.add_to_payroll_list(payroll_id)
				if res:
					return True, "Done."
				else:
					raise
			else: 
				raise
		except Exception as err:
			sql = """DROP TABLE IF EXISTS payroll_{0};""".format(payroll_id)
			curs.execute(sql)
			return False, [create_msg, insert_msg]
		finally:
			curs.close()

	def update_payroll_IDs(self, payroll_id):
		try:
			curs = self.mysql.get_db().cursor()
			sql = """INSERT INTO payroll_{0} (EmployeeID) (SELECT EmployeeID FROM tbl_employee 
				WHERE EmployeeID NOT IN (SELECT EmployeeID FROM payroll_{1}));""".format(payroll_id, payroll_id)
			curs.execute(sql)
			self.mysql.get_db().commit()
			return True, "Done."
		except Exception as err:
			self.mysql.get_db().rollback()
			return False, err
		finally:
			curs.close()

	def delete_employee_payroll(self, payroll_id):
		try:
			curs = self.mysql.get_db().cursor()
			sql = """DROP TABLE IF EXISTS payroll_{0};""".format(payroll_id)
			curs.execute(sql)
			sql = "DELETE FROM tbl_payrolls WHERE PayrollID = '{}'".format(payroll_id)
			curs.execute(sql)
			curs.close()
			self.mysql.get_db().commit()
			return True, "Done."
		except Exception as err:
			return False, err

		finally:
			curs.close()


	def download_employee_payroll(self, payroll_id):
		employee_payroll = self.get_employee_payroll(payroll_id)
		fpath = "./temp/payroll_{0}.xlsx".format(payroll_id)
		if os.path.exists(fpath):
			os.remove(fpath)
		payroll_sheet = "Payroll"
		payroll = xlsxwriter.Workbook(fpath)
		sheet = payroll.add_worksheet(payroll_sheet)
		# Write header
		header = ("EmployeeID", "Full Name", "Department", "Title", "Base Salary", "Over Time", "Allowance", \
			"Project Bonus", "Advance", "Unpaid Leave", "Total")
		for i, h in enumerate(header):
			sheet.write(0, i, h)
		for row, item in enumerate(employee_payroll):
			for col, val in enumerate(item.values()):
				sheet.write(row + 1, col, val)
		payroll.close()
		return fpath