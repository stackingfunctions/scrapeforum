from latesttopic import LatestTopic
from metadata import Batch, ScrapeError

import configparser
import sys
import os

from time import gmtime, strftime

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from urllib.error import HTTPError
from urllib.request import urlopen

from bs4 import BeautifulSoup


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

# Save latest topics entries to DB
try:

    # TODO move to Config object
    # Read config file
    try:
        config = initConfig()
        # Get DB configuration
        db = config['Destination DB']
    except KeyError as e:
        # TODO try to send error email and log to screen
        raise e

    # Set up DB connection
    engine = create_engine("mysql://" + db['user'] + ":" + db['passwd'] + "@" + db['host'] + "/" + db['dbName'] + "?charset=" + db['charset'], echo=(db['echo']=='True'))

    # Create missing tables
    Batch.metadata.create_all(engine)
    LatestTopic.metadata.create_all(engine)

    # Set uo and open a session
    conn = engine.connect()
    Session = sessionmaker(bind=engine)
    session = Session()

    # Create a Batch object to be logged in the DB
    batch = Batch(scriptStartTime=strftime("%Y-%m-%d %H:%M:%S", gmtime()), scriptName=os.path.basename(sys.argv[0]))

    # Insert a new Batch entry and get the auto nenerated ID value
    # TODO: I believe there should be an easier way to do this, but the search took too much time
    session.add(batch)
    session.flush()
    session.refresh(batch)

    # Parse start page
    URL =  config['Website']["startURL"]
    bsObj = parseURL(URL)



    # Check if parsing was successful
    if bsObj == None:
        # Log parsing error in DB
        session.add(ScrapeError(batchId=batch.id, errorString="Failed to parse start page - URL='" + URL + "'"))
        # TODO try to send error email and log to screen
        sys.exit()

    else:
        # Scrape start page
        latestTable = bsObj.find("table", {"id":"kflattable"})
        latestRows = latestTable.findAll({"tr"})

        for latestRow in latestRows :
            latestTopic = LatestTopic(latestRow)
            session.add(latestTopic)

finally:
    # Close the Batch in the DB
    session.query(Batch).filter_by(id=batch.id).update({"scriptEndTime": strftime("%Y-%m-%d %H:%M:%S", gmtime())})
    session.commit()

    # Close and clean up connections
    conn.close()
    engine.dispose()