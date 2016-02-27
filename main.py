# ----- Imports ----- #

from flask import Flask, g, render_template, url_for
import sqlite3
from threading import Thread

from scan import sync


# ----- Constants ----- #

# The database schema file.
DB_SCHEMA = 'schema.sql'

# The database file.
DB_FILE = 'media.db'


# ----- Setup ----- #

# The app object.
app = Flask(__name__)


# ----- Functions ----- #

def get_db():

	"""Retrieves a database connection."""

	db = getattr(g, '_database', None)

	if db is None:

		db = g._database = sqlite3.connect(DB_FILE)
		db.row_factory = sqlite3.Row

	return db


@app.teardown_appcontext
def close_connection(exception):

	"""Closes the database connection when app context is destroyed."""

	db = getattr(g, '_database', None)

	if db is not None:
		db.close()


def query_db(query, args=(), single_result=False):

	"""Queries the database."""

	cur = get_db().execute(query, args)

	results = cur.fetchall()
	cur.close()

	return (results[0] if results else None) if single_result else results


def init_db():

	"""Creates the database from a schema file."""

	with app.app_context():

		db = get_db()

		with app.open_resource(DB_SCHEMA, mode='r') as schema_file:
			db.cursor().executescript(schema_file.read())

		db.commit()


# ----- Routes ----- #

@app.route('/')
def index():

	"""Displays the homepage."""

	return render_template('index.html')


@app.route('/movies')
def movies():

	"""Displays a list of movies."""

	result_list = query_db('SELECT * FROM movies')
	movie_list = [dict(row) for row in result_list]

	for item in movie_list:
		item['url'] = url_for('.movie', movie_id=item['id'])

	return render_template('movies.html', movies=movie_list)


@app.route('/movies/<movie_id>')
def movie(movie_id):

	"""Displays a movie page."""

	info = query_db('SELECT * FROM movies WHERE id = ?', (movie_id,), True)

	return render_template('movie.html', movie=info)


@app.route('/tv_shows')
def tv_shows():

	"""Displays a list of TV shows."""

	result_list = query_db('SELECT * FROM tv_shows')
	show_list = [dict(row) for row in result_list]

	for item in show_list:
		item['url'] = url_for('.tv_show', show_id=item['id'])

	return render_template('tv_shows.html', shows=show_list)


@app.route('/tv_shows/<show_id>')
def tv_show(show_id):

	"""Displays a TV show page."""

	info = query_db('SELECT * FROM tv_shows WHERE id = ?', (show_id,), True)
	episodes = query_db('SELECT * FROM episodes WHERE show = ?', (show_id,))

	return render_template('show.html', name=info['name'], episodes=episodes)


@app.route('/scan', methods=['POST'])
def scan():

	"""Starts thread to scan media directories and populate database."""

	scan_thread = getattr(g, '_scan_thread', None)

	if not scan_thread or not scan_thread.isAlive():
		g._scan_thread = Thread(target=sync, args=(DB_FILE,))
		g._scan_thread.start()

	return 'Accepted', 202


# ----- Main ----- #

if __name__ == '__main__':

	init_db()
	app.run(debug=True)
