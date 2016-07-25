import configparser
from urllib.error import HTTPError
from urllib.request import urlopen

import pymysql
from bs4 import BeautifulSoup

import latesttopic

from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker

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


# Save latest topics entries to DB
try:
    # TODO: refactor to use sqlalchemy

    # Read config file
    try:
        config = initConfig()
        # Get DB configuration
        db = config['Destination DB']
    except KeyError as e:
        # TODO log error to db - in note?
        raise e

    # Set up DB connection
    pconn = pymysql.connect(host=db['host'], user=db['user'], passwd=db['passwd'], db=db['dbName'], charset=db['charset'])
    cur = pconn.cursor()
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


        engine = create_engine("mysql://" + db['user'] + ":" + db['passwd'] + "@" + db['host'] + "/" + db['dbName'] + "?charset=" + db['charset'], echo=True)
        conn = engine.connect()
        metadata = MetaData() # it is best prectice to share one MetaData object trhough all mapped classes to resolve foreign key references flawlessly - in this case we don't have FK, but le's keep the best practice
        Session = sessionmaker(bind=engine)

        for latestRow in latestRows :
            latestTopic = latesttopic.LatestTopic(latestRow)
            session = Session()
            session.add(latestTopic)
            session.commit()
            #latestTopic.insert2db(conn, metadata)
            #latestTopic.display()
            print(repr(latestTopic))

finally:
    if cur != None:
        # Record the end of runnting the script
        cur.execute("UPDATE script_run SET script_end_time = CURRENT_TIMESTAMP WHERE id =\"%s\"", (scriptRunId))
        cur.connection.commit()

        # Close connection
        cur.close()

    if pconn != None:
        pconn.close()

    conn.close()
    engine.dispose()