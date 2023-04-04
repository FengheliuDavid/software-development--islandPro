
"""
Columbia's COMS W4111.001 Introduction to Databases
Example Webserver
To run locally:
    python server.py
Go to http://localhost:8111 in your browser.
A debugger such as "pdb" may be helpful for debugging.
Read about it online.
"""
import os
  # accessible as a variable in index.html:
from sqlalchemy import *
from sqlalchemy.pool import NullPool
from flask import Flask, request, render_template, g, redirect, Response
import json

tmpl_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
app = Flask(__name__, template_folder=tmpl_dir)

DATABASE_USERNAME = "fl2625"
DATABASE_PASSWRD = "6068"
DATABASE_HOST = "34.148.107.47" # change to 34.28.53.86 if you used database 2 for part 2
DATABASEURI = f"postgresql://{DATABASE_USERNAME}:{DATABASE_PASSWRD}@{DATABASE_HOST}/project1"

engine = create_engine(DATABASEURI)


@app.before_request
def before_request():
	try:
		g.conn = engine.connect()
	except:
		print("uh oh, problem connecting to database")
		import traceback; traceback.print_exc()
		g.conn = None

@app.teardown_request
def teardown_request(exception):
	try:
		g.conn.close()
	except Exception as e:
		pass


# see for routing: https://flask.palletsprojects.com/en/1.1.x/quickstart/#routing
# see for decorators: http://simeonfranklin.com/blog/2012/jul/1/python-decorators-in-12-steps/
@app.route('/')
def index():
	return render_template("index.html")

#given island name, return information
@app.route('/island_info', methods=['POST'])
def island_info():
	island_name = request.form.get('isl_info')
	cursor = g.conn.execute(text("SELECT * FROM island WHERE island_name = "+ "'" + island_name + "'"))

	iinfo = []
	for result in cursor:
		iinfo.append(result)
	cursor.close()
	return render_template("index.html", iinfo= iinfo)

#given filter input, return satisfied islands
@app.route('/filter_islands')
def filter_islands():
	query_column = ['country', 'ocean', 'language', 'attraction_type', 'area', 'population']
	fil_dict = {}
	for i in query_column:
		if request.args.get(i, ''):
			fil_dict[i] = request.args.get(i, '')
		
	query_str = "SELECT DISTINCT island.* FROM island, tourism_attraction WHERE island.island_id = tourism_attraction.island_id AND "
	for k, v in fil_dict.items():
		if k in ['area','population']: #include a range
			if v[-1] == '+':
				lb = v[1:-1]
				query_str = query_str + k + ">=" + lb + " AND "
			else:
				dash_index = v.index('-')
				lb = v[1:dash_index]
				ub = v[dash_index+1:]
				query_str = query_str + k + ">=" + lb + " AND " + k + "<" + ub + " AND "
		else: #not include a range
			query_str = query_str + k + "=" + "'"+v+"'" + " AND "
	query_str = query_str[:-5]
	
	cursor = g.conn.execute(text(query_str))
	
	fnames = []
	for result in cursor:
		fnames.append(result)
	cursor.close()
	return render_template("index.html", fdata = fnames)

	
	
"""below code takes an island name and return the tourism, restaurant, etc. So, when show the result, could also get these"""	
"""tourism.html"""
@app.route('/tourism/<island>')
def tourism(island):
	#tourism
	query_str = "SELECT tourism_attraction.* FROM tourism_attraction, island WHERE island.island_id = tourism_attraction.island_id AND island_name =" + "'"+island+"'"
	cursor = g.conn.execute(text(query_str))
	tourism_info = []
	for result in cursor:
		tourism_info.append(result)
	cursor.close()
	#tour
	query_str2 = "SELECT tour.* FROM tour, island WHERE island.island_id = tour.island_id AND island_name =" + "'"+island+"'"
	cursor2 = g.conn.execute(text(query_str2))
	tour_info = []
	for result in cursor2:
		tour_info.append(result)
	cursor2.close()
	return render_template('tourism.html', tourism_info= tourism_info, tour_info= tour_info, island = island)

"""resta.html"""
@app.route('/resta/<island>')
def resta(island):
	query_str = "SELECT restaurant.* FROM restaurant, island WHERE island.island_id = restaurant.island_id AND island_name =" + "'"+island+"'"
	cursor = g.conn.execute(text(query_str))

	resta_info = []
	for result in cursor:
		resta_info.append(result)
	cursor.close()

	return render_template('resta.html', resta_info= resta_info, island = island)

"""hotel.html"""
@app.route('/hotel/<island>')
def hotel(island):
	query_str = "SELECT hotel.* FROM hotel, island WHERE island.island_id = hotel.island_id AND island_name =" + "'"+island+"'"
	cursor = g.conn.execute(text(query_str))

	hotel_info = []
	for result in cursor:
		hotel_info.append(result)
	cursor.close()
	
	return render_template('hotel.html', hotel_info= hotel_info, island = island)
	#return render_template('hotel.html', q = query_str)

"""airport.html"""
@app.route('/airport/<island>')
def airport(island):
	query_str = "SELECT airport.* FROM airport, island WHERE island.island_id = airport.island_id AND island_name =" + "'"+island+"'"
	cursor = g.conn.execute(text(query_str))
	
	airport_info = []
	for result in cursor:
		airport_info.append(result)
	cursor.close()

	return render_template('airport.html', airport_info= airport_info, island = island)

"""below codes are about the budget function"""
@app.route('/hotel-add-to-budget', methods=['POST'])
def hotel_add_to_budget():
	event_type = request.form['hotel_name']
	event_type =  event_type[:1]
	event_price = request.form['price_level']
	event_price = float(event_price)*50
	params = {}
	params["event_type"] = event_type
	params["event_price"] = event_price
	with engine.begin() as connection:
		connection.execute(text("INSERT INTO budget VALUES (:event_type, :event_price)"), params)
	return redirect(request.referrer)

@app.route('/resta-add-to-budget', methods=['POST'])
def resta_add_to_budget():
	event_type = request.form['resta_name']
	event_type =  event_type[:1]
	event_price = request.form['price_level']
	event_price = float(event_price)*10
	params = {}
	params["event_type"] = event_type
	params["event_price"] = event_price
	with engine.begin() as connection:
		connection.execute(text("INSERT INTO budget VALUES (:event_type, :event_price)"), params)
	return redirect(request.referrer)
	
@app.route('/tourism-add-to-budget', methods=['POST'])
def tourism_add_to_budget():
	event_type = request.form['tourism_name']
	event_type =  event_type[:1]
	event_price = request.form['price_level']
	event_price = event_price
	params = {}
	params["event_type"] = event_type
	params["event_price"] = event_price
	with engine.begin() as connection:
		connection.execute(text("INSERT INTO budget VALUES (:event_type, :event_price)"), params)
	return redirect(request.referrer)
"""
@app.route('/budget')
def budget():
	cursor = g.conn.execute("SELECT SUM(price) FROM budget")
	sum_budget = cursor.fetchone()[0]
	cursor.close()
	return render_template("budget.html", sum_budget =sum_budget)
"""
@app.route('/delete_budget', methods=['POST'])
def delete_budget():
    with engine.begin() as connection:
	connection.execute(text("DELETE FROM budget"))
    return redirect('/budget')

@app.route('/budget')
def budget():
    cursor = g.conn.execute(text("SELECT event_type, SUM(price) FROM budget GROUP BY event_type"))
    rows = cursor.fetchall()
    cursor.close()
    event_types = []
    prices = []
    for row in rows:
        event_types.append(row[0])
        prices.append(row[1])
    sum_budget = sum(prices)
    return render_template("budget.html", sum_budget=sum_budget, event_types=event_types, prices=prices)

	

# Example of adding new data to the database
@app.route('/add', methods=['POST'])
def add():
	# accessing form inputs from user
	name = request.form['name']
	
	# passing params in for each variable into query
	params = {}
	params["new_name"] = name
	g.conn.execute(text('INSERT INTO test(name) VALUES (:new_name)'), params)
	g.conn.commit()
	return redirect('/')


@app.route('/login')
def login():
	abort(401)
	this_is_never_executed()


if __name__ == "__main__":
	import click

	@click.command()
	@click.option('--debug', is_flag=True)
	@click.option('--threaded', is_flag=True)
	@click.argument('HOST', default='0.0.0.0')
	@click.argument('PORT', default=8111, type=int)
	def run(debug, threaded, host, port):
		"""
		This function handles command line parameters.
		Run the server using:
			python server.py
		Show the help text using:
			python server.py --help
		"""

		HOST, PORT = host, port
		print("running on %s:%d" % (HOST, PORT))
		app.run(host=HOST, port=PORT, debug=debug, threaded=threaded)

run()
