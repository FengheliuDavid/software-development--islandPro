
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

tmpl_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
app = Flask(__name__, template_folder=tmpl_dir)

DATABASE_USERNAME = "fl2625"
DATABASE_PASSWRD = "6068"
DATABASE_HOST = "34.148.107.47" # change to 34.28.53.86 if you used database 2 for part 2
DATABASEURI = f"postgresql://{DATABASE_USERNAME}:{DATABASE_PASSWRD}@{DATABASE_HOST}/project1"

engine = create_engine(DATABASEURI)

# Example of running queries in your database
# Note that this will probably not work if you already have a table named 'test' in your database, containing meaningful data. This is only an example showing you how to run queries in your database using SQLAlchemy.
#
#with engine.connect() as conn:
#	create_table_command = """
#	CREATE TABLE IF NOT EXISTS test (
#		id serial,
#		name text
#	)
#	"""
#	res = conn.execute(text(create_table_command))
#	insert_table_command = """INSERT INTO test(name) VALUES ('grace hopper'), ('alan turing'), ('ada lovelace')"""
#	res = conn.execute(text(insert_table_command))
#	# you need to commit for create, insert, update queries to reflect
#	conn.commit()


@app.before_request
def before_request():
	"""
	This function is run at the beginning of every web request 
	(every time you enter an address in the web browser).
	We use it to setup a database connection that can be used throughout the request.
	The variable g is globally accessible.
	"""
	try:
		g.conn = engine.connect()
	except:
		print("uh oh, problem connecting to database")
		import traceback; traceback.print_exc()
		g.conn = None

@app.teardown_request
def teardown_request(exception):
	"""
	At the end of the web request, this makes sure to close the database connection.
	If you don't, the database could run out of memory!
	"""
	try:
		g.conn.close()
	except Exception as e:
		pass


#
# @app.route is a decorator around index() that means:
#   run index() whenever the user tries to access the "/" path using a GET request
#
# If you wanted the user to go to, for example, localhost:8111/foobar/ with POST or GET then you could use:
#
#       @app.route("/foobar/", methods=["POST", "GET"])
#
# PROTIP: (the trailing / in the path is important)
# 
# see for routing: https://flask.palletsprojects.com/en/1.1.x/quickstart/#routing
# see for decorators: http://simeonfranklin.com/blog/2012/jul/1/python-decorators-in-12-steps/
#
@app.route('/')
def index():
	"""
	request is a special object that Flask provides to access web request information:
	request.method:   "GET" or "POST"
	request.form:     if the browser submitted a form, this contains the data in the form
	request.args:     dictionary of URL arguments, e.g., {a:1, b:2} for http://localhost?a=1&b=2
	See its API: https://flask.palletsprojects.com/en/1.1.x/api/#incoming-request-data
	

	# DEBUG: this is debugging code to see what request looks like
	print(request.args)


	#
	# example of a database query
	#
	#lan=request.form["language"]
	#print("lan")
	want = 'Bali'
	cursor = g.conn.execute("SELECT island_id FROM island WHERE island_name = "+ "'" + want + "'")

	names = []
	for result in cursor:
		names.append(result[0])
	print("names:", names)
	cursor.close()

	#
	# Flask uses Jinja templates, which is an extension to HTML where you can
	# pass data to a template and dynamically generate HTML based on the data
	# (you can think of it as simple PHP)
	# documentation: https://realpython.com/primer-on-jinja-templating/
	#
	# You can see an example template in templates/index.html
	#
	# context are the variables that are passed to the template.
	# for example, "data" key in the context variable defined below will be 
	# accessible as a variable in index.html:
	#
	#     # will print: [u'grace hopper', u'alan turing', u'ada lovelace']
	#     <div>{{data}}</div>
	#     
	#     # creates a <div> tag for each element in data
	#     # will print: 
	#     #
	#     #   <div>grace hopper</div>
	#     #   <div>alan turing</div>
	#     #   <div>ada lovelace</div>
	#     #
	#     {% for n in data %}
	#     <div>{{n}}</div>
	#     {% endfor %}
	#
	context = dict(data = names)
	"""

	#
	# render_template looks in the templates/ folder for files.
	# for example, the below file reads template/index.html
	#
	return render_template("index.html")
	#return render_template("index.html", **context)

#
# This is an example of a different path.  You can see it at:
# 
#     localhost:8111/another
#
# Notice that the function name is another() rather than index()
# The functions for each app.route need to have different names
#
@app.route('/budget')
def another():
	return render_template("budget.html")


@app.route('/island_info', methods=['POST'])
def island_info():
	island_name = request.form.get('isl_info')
	cursor = g.conn.execute("SELECT * FROM island WHERE island_name = "+ "'" + island_name + "'")

	iinfo = []
	for result in cursor:
		iinfo.append(result)
	cursor.close()
	return render_template("index.html", iinfo= iinfo)


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
	
	cursor = g.conn.execute(query_str)
	
	fnames = []
	for result in cursor:
		#fnames.append(result[0])
		fnames.append(result)
	cursor.close()
	#context = dict(fdata = fnames)
	return render_template("index.html", fdata = fnames, q_str = query_str)
	#return render_template("index.html", q_str = query_str)
	
	
		
"""tourism.html"""
@app.route('/tourism/<island>')
def tourism(island):
	#tourism
	query_str = "SELECT tourism_attraction.* FROM tourism_attraction, island WHERE island.island_id = tourism_attraction.island_id AND island_name =" + "'"+island+"'"
	cursor = g.conn.execute(query_str)
	tourism_info = []
	for result in cursor:
		tourism_info.append(result)
	cursor.close()
	#tour
	query_str2 = "SELECT tour.* FROM tour, island WHERE island.island_id = tour.island_id AND island_name =" + "'"+island+"'"
	cursor2 = g.conn.execute(query_str2)
	tour_info = []
	for result in cursor2:
		tour_info.append(result)
	cursor2.close()
	return render_template('tourism.html', tourism_info= tourism_info, tour_info= tour_info, island = island)

"""resta.html"""
@app.route('/resta/<island>')
def resta(island):
	query_str = "SELECT restaurant.* FROM restaurant, island WHERE island.island_id = restaurant.island_id AND island_name =" + "'"+island+"'"
	cursor = g.conn.execute(query_str)

	resta_info = []
	for result in cursor:
		resta_info.append(result)
	cursor.close()

	return render_template('resta.html', resta_info= resta_info, island = island)

"""hotel.html"""
@app.route('/hotel/<island>')
def hotel(island):
	query_str = "SELECT hotel.* FROM hotel, island WHERE island.island_id = hotel.island_id AND island_name =" + "'"+island+"'"
	cursor = g.conn.execute(query_str)

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
	cursor = g.conn.execute(query_str)
	
	airport_info = []
	for result in cursor:
		airport_info.append(result)
	cursor.close()

	return render_template('airport.html', airport_info= airport_info, island = island)

"""budget"""
@app.route('/hotel-add-to-budget', methods=['POST'])
def hotel_add_to_budget():
	event_type = request.form['hotel_name']
	event_type =  event_type[:3]
	event_price = request.form['price_level']
	event_price = float(event_price)*50
	params = {}
	params["event_type"] = event_type
	params["event_price"] = event_price
	with engine.begin() as connection:
		connection.execute(text("INSERT INTO budget VALUES (:event_type, :event_price)"), params)
	return '<html><body><h1>Added!</h1></body></html>'

@app.route('/resta-add-to-budget', methods=['POST'])
def resta_add_to_budget():
	event_type = request.form['resta_name']
	event_type =  event_type[:3]
	event_price = request.form['price_level']
	event_price = float(event_price)*10
	params = {}
	params["event_type"] = event_type
	params["event_price"] = event_price
	with engine.begin() as connection:
		connection.execute(text("INSERT INTO budget VALUES (:event_type, :event_price)"), params)
	return '<html><body><h1>Added!</h1></body></html>'
	
@app.route('/tourism-add-to-budget', methods=['POST'])
def tourism_add_to_budget():
	event_type = request.form['tourism_name']
	event_type =  event_type[:3]
	event_price = request.form['price_level']
	event_price = event_price
	params = {}
	params["event_type"] = event_type
	params["event_price"] = event_price
	with engine.begin() as connection:
		connection.execute(text("INSERT INTO budget VALUES (:event_type, :event_price)"), params)
	return '<html><body><h1>Added!</h1></body></html>'
	
	

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
