import configparser
from urllib.error import HTTPError
from urllib.request import urlopen

import pymysql
from bs4 import BeautifulSoup

import latesttopic


#############################
# Internal helper functions #
#############################

# Prints an attribute after announcing it
def _printResult(attribute, attributeName):
    print("\n*****\n  " + attributeName + "\n*****\n\n")
    print(attribute)

#############
# Functions #
#############

# @TODO: save failure in DB

def parseURL(URL):
    try:
        html = urlopen(URL)
    except HTTPError as e:
        print("[ERROR] HTTPError- Opening URL failed. Error code:'" + repr(e.code) + "', URL:'" + URL + "'")
    except Exception as e:
        print("[ERROR] Exception - Other exception found:\n" + repr(e))
        return None
    else:
        try:
            return BeautifulSoup(html.read())
        except Exception as e:
            print("[ERROR] Parsing HTML failed. Error:\n" + repr(e))
            return None


def initConfig():
    config = configparser.ConfigParser()
    config.read('../config/config.ini')
    return config




#################
# Scraping body #
#################

scriptName = "scrapeforum.py"

try:
    # Read config file
    config = initConfig()

    # Get DB configuration
    db = config['Destination DB']

    # Set up DB connection
    conn = pymysql.connect(host=db['host'], user=db['user'], passwd=db['passwd'], db=db['dbName'], charset=db['charset'])
    cur = conn.cursor()
    cur.execute("USE " + db['schema'])
    cur.execute("SET SESSION wait_timeout=" + db['sessionTimeOut'])

    # Record the start of running script and hold onto the auto incremented ID
    cur.execute("INSERT INTO script_run(script_name) VALUES ('" + scriptName + "')")
    cur.execute("SELECT LAST_INSERT_ID()")
    scriptRunId = cur.fetchone()
    cur.connection.commit()

    # Parse start page
    URL =  config['Website']["startURL"]
    bsObj = parseURL(URL)

    # Check if parsing was successful
    if bsObj == None:
        # Report error
        cur.execute("INSERT INTO exceptions(function_name, exception_type, exception_string, script_name, exception_time) VALUES('main', 'QUIET ERROR', 'BeautifulSoup failed to parse " + URL + "', '" +scriptName + "', CURRENT_TIMESTAMP)")
        cur.connection.commit()

    else:
        # Scrape URL
        latestTable = bsObj.find("table", {"id":"kflattable"})
        latestRows = latestTable.findAll({"tr"})

        for latestRow in latestRows :
            latestEntry = latesttopic.LatestTopic(latestRow)
            latestEntry.display()

finally:
    if cur != None:
        # Record the end of runnting the script
        cur.execute("UPDATE script_run SET script_end_time = CURRENT_TIMESTAMP WHERE id =\"%s\"", (scriptRunId))
        cur.connection.commit()

        # Close connection
        cur.close()

    if conn != None:
        conn.close()
