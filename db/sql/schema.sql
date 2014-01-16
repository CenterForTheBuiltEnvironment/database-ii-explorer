CREATE TABLE building (
  id integer primary key,
  sourceid integer,
  system text,
  city text,
  description text,
  FOREIGN KEY(sourceid) REFERENCES source(id)
);
CREATE TABLE data (
  id integer primary key,
  respid integer,
  fieldid text,
  value real,
  FOREIGN KEY(respid) REFERENCES response(id),
  FOREIGN KEY(fieldid) REFERENCES field(id)
);
CREATE TABLE field (
  id text primary key,
  description text,
  unit text
);
CREATE TABLE participant (
  id integer primary key,
  bldgid integer,
  age integer,
  sex text,
  FOREIGN KEY(bldgid) REFERENCES building(id)
);
CREATE TABLE response (
  id integer primary key,
  datetime integer,
  partid integer,
  FOREIGN KEY(partid) REFERENCES participant(id)
);
CREATE TABLE source (
  id integer primary key,
  description text,
  contact_name text,
  contact_email text,
  url text
);
CREATE INDEX data_respid_idx ON data (respid);
