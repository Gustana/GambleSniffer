BEGIN TRANSACTION;

CREATE TABLE prediction(
	web_url TEXT PRIMARY KEY,
	is_gambling_site BOOLEAN NULL,
	scraping_time TIMESTAMP NOT NULL,
	is_error BOOLEAN NOT NULL
);

CREATE TABLE error_report(
	web_url TEXT PRIMARY KEY,
	description TEXT NOT NULL
);

CREATE TABLE dataset(
	web_url TEXT PRIMARY KEY,
	scraping_time TIMESTAMP NOT NULL,
	is_gambling_site BOOLEAN NOT NULL
);

COMMENT ON TABLE dataset is 'contains data from manual scraping for modeling';

COMMIT;