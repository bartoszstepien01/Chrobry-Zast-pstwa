CREATE TABLE date (
    id integer NOT NULL,
    date date,
    current_substitutions json
);

CREATE TABLE message (
    id integer NOT NULL,
    name character varying,
    value integer
);

CREATE TABLE setting (
    id integer NOT NULL,
    name character varying,
    value character varying
);

CREATE TABLE "user" (
    id character varying(100) NOT NULL,
    grade character varying(5)
);

INSERT INTO date (id, date, current_substitutions) VALUES (1, '1970-01-01', '{}');

INSERT INTO message (id, name, value) VALUES (1, 'sent', 0);
INSERT INTO message (id, name, value) VALUES (2, 'received', 0);

INSERT INTO setting (id, name, value) VALUES (1, 'substitutions_url', 'http://www.chrobry1lo.nazwa.pl/chrobry/zastepstwa2022/');
INSERT INTO setting (id, name, value) VALUES (2, 'metadata_url', 'http://www.chrobry1lo.nazwa.pl/chrobry/plan092020/timetable.xml');
INSERT INTO setting (id, name, value) VALUES (3, 'dates_url', 'http://www.chrobry1lo.nazwa.pl/chrobry/zastepstwa2022/subst_left.htm');
INSERT INTO setting (id, name, value) VALUES (4, 'hours', '7:10-7:55,8:00-8:45,8:55-9:40,9:50-10:35,10:45-11:30,11:40-12:25,12:35-13:20,13:30-14:15,14:20-15:05,16:00-16:45');
INSERT INTO setting (id, name, value) VALUES (5, 'grades', '1a,1b,1c,1d,2a,2b,2c,2d,2e,3a,3b,3c,3d,3e');