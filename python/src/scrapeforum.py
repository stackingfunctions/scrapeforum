from latesttopic import LatestTopic
from metadata import Batch, ScrapeError
from configurator import Configurator
from constants import EMAIL_NOTIFICATION, EMAIL_ERROR
from mailer import Mailer

import sys
import os

from time import gmtime, strftime
from datetime import datetime

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from urllib.error import HTTPError
from urllib.request import urlopen

from bs4 import BeautifulSoup


#############
# Functions #
#############

def parseURL(URL):
    emailSubject = "Failed to parse URL"
    try:
        html = urlopen(URL)
    except HTTPError as e:
        errorString = "HTTPError - Opening URL failed. Error code:'" + repr(e.code) + "', URL:'" + URL + "'"
        print("[ERROR] " + errorString)
        Mailer(EMAIL_ERROR).send(emailSubject, errorString)

    except Exception as e:
        errorString = "Exception - Other exception found:\n" + repr(e)
        print("[ERROR] " + errorString)
        Mailer(EMAIL_ERROR).send(emailSubject, errorString)
        return None

    else:
        try:
            return BeautifulSoup(html.read())
        except Exception as e:
            errorString = "Parsing HTML failed. Error:\n" + repr(e)
            print("[ERROR] " + errorString)
            Mailer(EMAIL_ERROR).send(emailSubject, errorString)
            return None



#################
# Scraping body #
#################

# Read configuration
try:
    config = Configurator()
    db = config.getDb()
    URL =  config.getURL()["startURL"]

except:
    errorString = "Unable to read configuration from '../config/config.ini'. Make sure you are running the script from 'scrapeforum' folder."
    print("[ERROR] " + errorString)
    Mailer(EMAIL_ERROR).send("Unable to read configuration", errorString)
    os._exit(1)

# Send notification email about start
Mailer(EMAIL_NOTIFICATION).send("Scraping started", "Scraping started for " + URL + " at " + datetime.strftime(datetime.now(), '%Y-%m-%d %H:%M:%S'))

# Connect to database
try:
    # Set up DB connection
    connectionString = "mysql://" + db['user'] + ":" + db['passwd'] + "@" + db['host'] + "/" + db['dbName'] + "?charset=" + db['charset']
    engine = create_engine(connectionString, echo=(db['echo'] == 'True'))

    # Create missing tables
    Batch.metadata.create_all(engine)
    LatestTopic.metadata.create_all(engine)

    # Set up and open a session
    conn = engine.connect()
    Session = sessionmaker(bind=engine)
    session = Session()

except:
    Mailer(EMAIL_ERROR).send("Failed to connect to database", "Connection string: " + connectionString)
    raise

try:
    # Create a Batch object to be logged in the DB
    batch = Batch(scriptStartTime=strftime("%Y-%m-%d %H:%M:%S", gmtime()), scriptName=os.path.basename(sys.argv[0]))

    # Insert a new Batch entry and get the auto generated ID value
    # TODO: I believe there should be an easier way to do this, but the search took too much time
    session.add(batch)
    session.flush()
    session.refresh(batch)

    # Parse start page
    bsObj = parseURL(URL)

    # Check if parsing was successful
    if bsObj == None:
        # Log parsing error in DB
        session.add(ScrapeError(batchId=batch.id, errorString="Failed to parse start page - URL='" + URL + "'"))
        sys.exit()

    else:
        # Scrape start page
        latestTable = bsObj.find("table", {"id":"kflattable"})
        latestRows = latestTable.findAll({"tr"})

        for latestRow in latestRows:
            try:
                latestTopic = LatestTopic(latestRow, batch.id)
                session.add(latestTopic)
            except:
                # TODO: falis for an entry where username contains '@' character
                print("****************")
                print(repr(latestRow))
                #raise


    # Scraping was successful, so set success flag to true
    session.query(Batch).filter_by(id=batch.id).update({"success": 1})
    # Notify in email about successful scrape
    Mailer(EMAIL_NOTIFICATION).send("Scraping ended - OK", "Scraping ended for " + URL + " at " + datetime.strftime(datetime.now(), '%Y-%m-%d %H:%M:%S'))

except:
    # Notify in email about failed scrape
    Mailer(EMAIL_NOTIFICATION).send("Scraping ended - ERROR", "Scraping ended for " + URL + " at " + datetime.strftime(datetime.now(), '%Y-%m-%d %H:%M:%S'))

finally:
    # Close the Batch in the DB
    session.query(Batch).filter_by(id=batch.id).update({"scriptEndTime": strftime("%Y-%m-%d %H:%M:%S", gmtime())})
    session.commit()

    # Close and clean up connections
    conn.close()
    engine.dispose()

