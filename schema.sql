PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS source (
  key TEXT PRIMARY KEY,
  name TEXT NOT NULL,
  url TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS place (
  area TEXT PRIMARY KEY NOT NULL,
  area_name TEXT NOT NULL,
  timezone TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS source_area (
  key TEXT PRIMARY KEY NOT NULL,
  area TEXT NOT NULL,

  FOREIGN KEY(key) REFERENCES source(key),
  FOREIGN KEY(area) REFERENCES place(area)
);

INSERT OR IGNORE INTO source(key, name, url) VALUES
("gumeracha_weir", "Gumeracha Weir", "http://www.bom.gov.au/fwo/IDS60248/IDS60248.523755.tbl.shtml"),
("millbrook_reservoir", "Millbrook Reservoir", "http://www.bom.gov.au/fwo/IDS60248/IDS60248.523763.tbl.shtml");

INSERT OR IGNORE INTO place(area, area_name, timezone) VALUES
("adelaide", "Adelaide", "Australia/Adelaide");

INSERT OR IGNORE INTO source_area(key, area) VALUES
("gumeracha_weir", "adelaide"),
("millbrook_reservoir", "adelaide");
