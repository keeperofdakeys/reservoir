PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS state (
  state TEXT PRIMARY KEY NOT NULL,
  state_name TEXT NOT NULL,
  timezone TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS place (
  area TEXT PRIMARY KEY NOT NULL,
  area_name TEXT NOT NULL,
  state TEXT NOT NULL,

  FOREIGN KEY(state) REFERENCES state(state)
);

CREATE TABLE IF NOT EXISTS source (
  key TEXT PRIMARY KEY,
  name TEXT NOT NULL,
  area TEXT NOT NULL,
  url TEXT NOT NULL,

  FOREIGN KEY(area) REFERENCES place(area)
);

INSERT OR IGNORE INTO state(state, state_name, timezone) VALUES
("south_australia", "South Australia", "Australia/Adelaide");

INSERT OR IGNORE INTO place(area, area_name, state) VALUES
("torrens", "Torrens", "south_australia"),
("port_adelaide", "Port Adelaide", "south_australia"),
("patawalonga", "Patawalonga", "south_australia");

INSERT OR IGNORE INTO source(key, name, area, url) VALUES
("torrens_ds_glen_devon", "Torrens DS Glen Devon Rd", "torrens", "http://www.bom.gov.au/fwo/IDS60248/IDS60248.524026.tbl.shtml"),
("torrens_mt_pleasant", "Torrens at Mt Pleasant", "torrens", "http://www.bom.gov.au/fwo/IDS60248/IDS60248.523778.tbl.shtml"),
("mt_pleasant", "Mt Pleasant", "torrens", "http://www.bom.gov.au/fwo/IDS60248/IDS60248.523732.tbl.shtml"),
("millers_ck", "Millers CK at Forreston", "torrens", "http://www.bom.gov.au/fwo/IDS60248/IDS60248.523709.tbl.shtml"),
("gumeracha_weir", "Gumeracha Weir", "torrens", "http://www.bom.gov.au/fwo/IDS60248/IDS60248.523755.tbl.shtml"),
("cudlee_ck", "Cudlee Ck at Lobethal Rd", "torrens", "http://www.bom.gov.au/fwo/IDS60248/IDS60248.523700.tbl.shtml"),
("millbrook_reservoir", "Millbrook Reservoir", "torrens", "http://www.bom.gov.au/fwo/IDS60248/IDS60248.523763.tbl.shtml"),
("torrens_ds_hollands", "Torrens DS Hollands Ck", "torrens", "http://www.bom.gov.au/fwo/IDS60248/IDS60248.523777.tbl.shtml"),
("kangaroo_creek_dam0", "Kangaroo Creek Dam", "torrens", "http://www.bom.gov.au/fwo/IDS60248/IDS60248.523733.tbl.shtml"),
("sixth_ck_castambul", "Sixth Ck at Castambul", "torrens", "http://www.bom.gov.au/fwo/IDS60248/IDS60248.023852.tbl.shtml"),
("sixth_ck", "Sixth Ck", "torrens", "http://www.bom.gov.au/fwo/IDS60248/IDS60248.523745.tbl.shtml"),
("gorge_weir", "Gorge Weir", "torrens", "http://www.bom.gov.au/fwo/IDS60248/IDS60248.523742.tbl.shtml"),
("fifth_ck_athelstone", "Fifth Creek at Athelstone", "torrens", "http://www.bom.gov.au/fwo/IDS60248/IDS60248.023094.tbl.shtml"),
("third_ck_magill", "Third Ck at Magill", "torrens", "http://www.bom.gov.au/fwo/IDS60248/IDS60248.023132.tbl.shtml"),
("second_ck_stonyfell", "Second Ck at Stonyfell", "torrens", "http://www.bom.gov.au/fwo/IDS60248/IDS60248.023145.tbl.shtml"),
("first_ck_cleland", "First Ck at Cleland", "torrens", "http://www.bom.gov.au/fwo/IDS60248/IDS60248.523782.tbl.shtml"),
("first_ck_waterfall_gully", "First Ck at Waterfall Gully", "torrens", "http://www.bom.gov.au/fwo/IDS60248/IDS60248.523746.tbl.shtml"),
("first_ck_botanic_gdns", "First Ck Botanic Gdns", "torrens", "http://www.bom.gov.au/fwo/IDS60248/IDS60248.523041.tbl.shtml"),
("torrens_walkerville", "Torrens at Walkerville", "torrens", "http://www.bom.gov.au/fwo/IDS60248/IDS60248.523040.tbl.shtml"),
("torrens_holbrooks_rd", "Torrens at Holbrooks Rd", "torrens", "http://www.bom.gov.au/fwo/IDS60248/IDS60248.523044.tbl.shtml"),
("torrens_seaview_rd", "Torrens at Seaview Rd", "torrens", "http://www.bom.gov.au/fwo/IDS60248/IDS60248.523042.tbl.shtml"),
("little_para_reservoir", "Little Para Reservoir", "port_adelaide", "http://www.bom.gov.au/fwo/IDS60248/IDS60248.523112.tbl.shtml"),
("pt_adelaide", "Port Adelaide", "port_adelaide", "http://www.bom.gov.au/fwo/IDS60248/IDS60248.523004.tbl.shtml"),
("keswick_ck_vic_park", "Keswick Ck at Victoria Park", "patawalonga", "http://www.bom.gov.au/fwo/IDS60248/IDS60248.523010.tbl.shtml"),
("keswick_ck_unley", "Keswick Ck at Unley", "patawalonga", "http://www.bom.gov.au/fwo/IDS60248/IDS60248.023119.tbl.shtml"),
("keswick_ck_army", "Keswick Ck at Army Barracks", "patawalonga", "http://www.bom.gov.au/fwo/IDS60248/IDS60248.023115.tbl.shtml"),
("brownhill_ck_mitcham", "Brownhill Ck at Mitcham", "patawalonga", "http://www.bom.gov.au/fwo/IDS60248/IDS60248.523769.tbl.shtml"),
("brownhill_ck_hawthorn", "Brownhill Ck at Hawthorn", "patawalonga", "http://www.bom.gov.au/fwo/IDS60248/IDS60248.523101.tbl.shtml"),
("brownhill_ck_adelaide_ap", "Brownhill Ck at Adelaide Ap", "patawalonga", "http://www.bom.gov.au/fwo/IDS60248/IDS60248.523046.tbl.shtml"),
("minno_ck_coromandel", "Minno Ck at Coromandel Valley", "patawalonga", "http://www.bom.gov.au/fwo/IDS60248/IDS60248.523748.tbl.shtml"),
("sturt_below_minno", "Sturt below Minno", "patawalonga", "http://www.bom.gov.au/fwo/IDS60248/IDS60248.523766.tbl.shtml"),
("sturt_dam", "Sturt Dam", "patawalonga", "http://www.bom.gov.au/fwo/IDS60248/IDS60248.023136.tbl.shtml"),
("sturt_ck_marion", "Sturt Ck at Marion", "patawalonga", "http://www.bom.gov.au/fwo/IDS60248/IDS60248.023140.tbl.shtml"),
("little_para_fault", "Little Para R Us Fault", "patawalonga", "http://www.bom.gov.au/fwo/IDS60248/IDS60248.523057.tbl.shtml");
