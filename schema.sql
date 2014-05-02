PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS source (
  name TEXT PRIMARY KEY,
  prop_name TEXT,
  url TEXT
);

CREATE TABLE IF NOT EXISTS source_area (
  name TEXT,
  area TEXT,
  FOREIGN KEY(name) REFERENCES source(name)
);

INSERT OR IGNORE INTO source(name, prop_name, url) VALUES
("gumeracha_weir", "Gumeracha Weir", "http://www.bom.gov.au/fwo/IDS60248/IDS60248.523755.tbl.shtml"),
("millbrook_reservoir", "Millbrook Reservoir", "http://www.bom.gov.au/fwo/IDS60248/IDS60248.523763.tbl.shtml");

INSERT OR IGNORE INTO source_area(name, area) VALUES
("gumeracha_weir", "Adelaide"),
("millbrook_reservoir", "Adelaide");
