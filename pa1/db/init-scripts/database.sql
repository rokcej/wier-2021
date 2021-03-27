CREATE SCHEMA IF NOT EXISTS crawler;

CREATE TABLE crawler.site (
    id serial NOT NULL,
    domain varchar(500) NOT NULL,
    robots_content text,
    sitemap_content text,
    PRIMARY KEY (id)
);


CREATE TABLE crawler.page_type ( 
	code varchar(20) NOT NULL,	
	PRIMARY KEY (code)
);

CREATE TABLE crawler.page (
    id serial NOT NULL,
    site_id integer,
    page_type_code varchar(20) NOT NULL,
    "url" varchar(3000) NOT NULL,
    html_content text,
    html_hash varchar(32),
    http_status_code integer,
    accessed_time timestamp,
    PRIMARY KEY (id),
    FOREIGN KEY (site_id) REFERENCES crawler.site(id),
    FOREIGN KEY (page_type_code) REFERENCES crawler.page_type(code)
);

CREATE UNIQUE INDEX uidx_page_url ON crawler.page(url);
CREATE INDEX idx_page_site_id ON crawler.page(site_id); 

CREATE TABLE crawler.link (
    from_page integer NOT NULL,
    to_page integer NOT NULL,
    PRIMARY KEY (from_page, to_page),
    FOREIGN KEY (from_page) REFERENCES crawler.page(id),
    FOREIGN KEY (to_page) REFERENCES crawler.page(id)
);

CREATE TABLE crawler.image (
    id serial NOT NULL,
    page_id integer NOT NULL,
    "filename" varchar(255),
    content_type varchar(50),
    "data" bytea,
    accessed_time timestamp,
    PRIMARY KEY (id),
    FOREIGN KEY (page_id) REFERENCES crawler.page(id)
);

CREATE INDEX idx_image_page_id ON crawler.image(page_id);

CREATE TABLE crawler.data_type ( 
	code varchar(20) NOT NULL,	
	PRIMARY KEY (code)
);

CREATE TABLE crawler.page_data ( 
	id serial NOT NULL,
	page_id integer NOT NULL,
	data_type_code varchar(20),
	"data" bytea,
    PRIMARY KEY (id),
    FOREIGN KEY (page_id) REFERENCES crawler.page(id),
    FOREIGN KEY (data_type_code) REFERENCES crawler.data_type(code)
);

CREATE TABLE crawler.email (
    email varchar(255) NOT NULL,
    page_id integer NOT NULL,
    PRIMARY KEY (email),
    FOREIGN KEY (page_id) REFERENCES crawler.page(id)
);

CREATE TABLE crawler.tel (
    tel varchar(20) NOT NULL,
    page_id integer NOT NULL,
    PRIMARY KEY (tel),
    FOREIGN KEY (page_id) REFERENCES crawler.page(id)
);

INSERT INTO crawler.page_type VALUES 
	('HTML'),
	('BINARY'),
	('DUPLICATE'),
    ('UNAVAILABLE'),
    ('DISALLOWED'),
	('FRONTIER'),
    ('PROCESSING');

INSERT INTO crawler.data_type VALUES 
	('PDF'),
	('DOC'),
	('DOCX'),
    ('DOCM'),
	('PPT'),
	('PPTX'),
    ('PPTM'),
    ('XLS'),
    ('XLSX'),
    ('XLSM'),
    ('ZIP'),
    ('RAR');
