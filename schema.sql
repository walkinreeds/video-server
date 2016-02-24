CREATE TABLE IF NOT EXISTS movies
	(id INTEGER PRIMARY KEY, name TEXT, path TEXT);

CREATE TABLE IF NOT EXISTS tv_shows
	(id INTEGER PRIMARY KEY, name TEXT);

CREATE TABLE IF NOT EXISTS episodes
	(id INTEGER PRIMARY KEY, name TEXT, number INTEGER, season INTEGER, path TEXT, show INTEGER,
		FOREIGN KEY (show) REFERENCES show(id));
