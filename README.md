#Reservoir Levels
A small project to keep track of reservoir levels, as reported by the Australian Bureau of Meteorology. One script, "update.py" updates the database. The other, "reservoir.py" provides a web front-end for accessing the information.

The web front-end uses HTTP to download the data, and graph it using a javascript library (FLOT). IE8+, and any other browsers that have been released in the last few years should be supported. 


## Dependencies
* Python 3 compiled with sqlite support.
  * A few parts require different syntax for Python 2 vs 3, so 3 was chosen.
  * Tested with Python 3.3.
* sqlite3 >= 3.7.11 
  * The schema uses commas in INSERTs to insert multiple tuples, only supported in 3.7.11 and up. Without this, 3.6 is known to work.

###Python modules
* pytz
* Flask
  * Includes sub-dependencies jinja2, and werkzueg.
* BeautifulSoup4
  * Only required for updater.

## TODO
* For scalability, csv files should be pre-generated by the updater. 
