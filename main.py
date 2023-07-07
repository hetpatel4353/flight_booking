import sqlite3
from flask import Flask, render_template, redirect, url_for, request
import copy
import re

ADMIN_USERNAME = 'admin'
ADMIN_PASSWORD = 'admin123'

app = Flask(__name__)


@app.route('/')
def landing():
	return render_template('landing.html')


@app.route('/usignup', methods=['GET', 'POST'])
def usignup():
	if request.method == "POST":
		uname = request.form['uname']
		password = request.form['password']
		email = request.form['email']
		passwordc = request.form['passwordc']

		if uname == "" or password == "" or email == "" or passwordc == "":
			return render_template("usignup.html", msg="Empty field")

		flag = 0
		while True:
			if (len(password) <= 8):
				flag = -1
				break
			elif not re.search("[a-z]", password):
				flag = -1
				break
			elif not re.search("[A-Z]", password):
				flag = -1
				break
			elif not re.search("[0-9]", password):
				flag = -1
				break
			elif not re.search("[_@$]", password):
				flag = -1
				break
			elif re.search("\s", password):
				flag = -1
				break
			else:
				flag = 0
				print("Valid Password")
				break

		if flag == -1:
			return render_template("usignup.html",msg="Password does not meet requirements")

		if password != passwordc:
			return render_template("usignup.html", msg="Password must be same")

		new = sqlite3.connect("simple.db")
		cursor = new.cursor()
		cursor.execute('select uname from user;')

		users = []
		for i in cursor.fetchall():
			users.append(i[0])
		new.close()
		if uname in users:
			return render_template("usignup.html", msg="Username already in use")
		new = sqlite3.connect("simple.db")
		cursor = new.cursor()
		cursor.execute(f"insert into user values ('{uname}','{password}','{email}')")
		new.commit()
		new.close()
		return redirect(url_for('ulogin'))

	return render_template("usignup.html")


@app.route('/ulogin', methods=['GET', 'POST'])
def ulogin():
	if request.method == 'POST' and 'uname' in request.form and 'password' in request.form:
		uname = request.form['uname']
		password = request.form['password']

		new = sqlite3.connect('simple.db')
		cursor = new.cursor()
		cursor.execute('select uname from user;')

		users = []
		for i in cursor.fetchall():
			users.append(i[0])
		new.close()
		if uname not in users:
			return render_template('ulogin.html', msg="No user found")

		new = sqlite3.connect('simple.db')
		cursor = new.cursor()
		cursor.execute(f"select pass from user where uname='{uname}'")

		pas = cursor.fetchall()[0][0]
		new.close()
		if password == pas:
			return render_template("user.html", name=uname)
		else:
			return render_template("ulogin.html", msg="Incorrect Password")

	return render_template("ulogin.html")


@app.route('/user<name>', methods=['GET', 'POST'])
def user(name):
	if request.method == 'POST':
		uname = request.form['uname']
		return render_template('user.html', name=uname)

	return render_template('user.html', name=name)


@app.route('/search_flights<name>', methods=['GET', 'POST'])
def search_flights(name):
	if request.method == 'POST':
		stdate = request.form.get('stdate', False)
		enddate = request.form.get('enddate', False)
		sttime = request.form.get('sttime', False)
		endtime = request.form.get('endtime', False)

		new = sqlite3.connect('simple.db')
		cursor = new.cursor()
		cursor.execute(
			f"select * from flight where fromdate >= '{stdate}' and todate <= '{enddate}' and fromTime >= '{sttime}' and toTime <= '{endtime}'")
		res = cursor.fetchall()
		avail = []
		for i in res:
			avail.append(i[-1])
		rem = []
		for i, d in enumerate(avail):
			if d <= 0:
				rem.append(i)
		res1 = copy.copy(res)
		print(rem)
		print(res1)
		c = 0
		for i in range(len(rem)):
			print(res1.pop(rem[i] - c))
			c += 1
		print(res)
		print(res1)
		new.close()
		return render_template('search_flights.html', res=res, res1=res1, stdate=stdate, enddate=enddate,
		                       sttime=sttime, endtime=endtime, name=name, fno=False)

	return render_template("search_flights.html", name=name)


@app.route('/book_flight<name>', methods=['GET', 'POST'])
def book_flight(name):
	if request.method == 'POST':
		fno = request.form.get('flights')

		new = sqlite3.connect('simple.db')
		cursor = new.cursor()
		cursor.execute(f"select * from flight where flightnumber = '{fno}'")
		res = cursor.fetchall()
		cursor.close()
		new.close()

	data = [name, fno]
	return render_template('book_flight.html', name=name, fno=fno, res=res, data=data)


@app.route('/success<data>', methods=['GET', 'POST'])
def success(data):
	if request.method == 'POST':
		name = data.split()[0][2:-2]
		fno = data.split()[1][1:-2]

		new = sqlite3.connect('simple.db')
		cursor = new.cursor()
		cursor.execute(f"insert into user_flights values('{name}','{fno}')")
		new.commit()
		new.close()
		new = sqlite3.connect('simple.db')
		cursor = new.cursor()
		cursor.execute(f"update flight set avail=avail-1 where flightnumber='{fno}' and avail>0")
		new.commit()
		new.close()
		new = sqlite3.connect('simple.db')
		cursor = new.cursor()
		cursor.execute(f"select * from flight where flightnumber='{fno}'")
		res = cursor.fetchall()
		cursor.close()
		new.close()
	return render_template('success.html', name=name, data=data, res=res)


@app.route('/my_bookings<name>', methods=['GET', 'POST'])
def my_bookings(name):
	if request.method == 'POST':
		new = sqlite3.connect('simple.db')
		cursor = new.cursor()
		cursor.execute(f"select * from user_flights where uname='{name}'")
		res = cursor.fetchall()
		flights = []
		for i in res:
			fno = i[1]
			cursor.execute(
				f"select flightnumber, start,dest, fromTime, toTime, fromdate, todate from flight where flightnumber='{fno}'")
			flights.append(cursor.fetchall())

		new.close()
	return render_template('my_bookings.html', name=name, res=res, flights=flights)


@app.route('/alogin', methods=['GET', 'POST'])
def alogin():
	if request.method == 'POST' and 'uname' in request.form and 'password' in request.form:
		uname = request.form['uname']
		password = request.form['password']
		if uname == ADMIN_USERNAME:
			if password == ADMIN_PASSWORD:
				return render_template('admin.html')
			else:
				return render_template('alogin.html', msg="Incorrect Password")
		else:
			return render_template('alogin.html', msg="Incorrect Username")

	return render_template("alogin.html")


@app.route('/admin')
def admin():
	return render_template('admin.html')


@app.route('/add_flight', methods=['GET', 'POST'])
def add_flight():
	if request.method == 'POST':
		flightno = request.form['flightno']
		start = request.form['start']
		dest = request.form['dest']
		fromtime = request.form['fromtime']
		totime = request.form['totime']
		fromdate = request.form['fromdate']
		enddate = request.form['enddate']
		avail = request.form['avail']
		new = sqlite3.connect('simple.db')
		cursor = new.cursor()
		cursor.execute(
			f"insert into flight(flightnumber,start,dest,fromTime,toTime,fromdate,todate,avail) values ('{flightno}','{start}','{dest}','{fromtime}','{totime}','{fromdate}','{enddate}','{avail}')")
		new.commit()
		new.close()
	return render_template('add_flight.html')


@app.route('/remove_flight', methods=['GET', 'POST'])
def remove_flight():
	if request.method == 'POST':
		flightno = request.form['flightno']
		new = sqlite3.connect('simple.db')
		cursor = new.cursor()
		cursor.execute(f"delete from flight where flightnumber='{flightno}'")
		new.commit()
		new.close()
	return render_template('remove_flight.html')


@app.route('/view_bookings', methods=['GET', 'POST'])
def view_bookings():
	if request.method == 'POST':
		fno = request.form['fno']

		new = sqlite3.connect('simple.db')
		cursor = new.cursor()
		cursor.execute(f"select uname from user_flights where flightno='{fno}'")
		res = cursor.fetchall()
		new.close()

		return render_template('view_bookings.html', res=res, fno=fno)

	return render_template('view_bookings.html')


if __name__ == '__main__':
	app.run(debug=True)
