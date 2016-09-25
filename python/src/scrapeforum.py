from latesttopic import LatestTopic
from metadata import Batch, ScrapeError
from configurator import Configurator
from mailer import Mailer
from mylogger import MyLogger
import constants


import sys
import os

from time import gmtime, strftime
from datetime import datetime

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from urllib.error import HTTPError
from urllib.request import urlopen

from bs4 import BeautifulSoup


logger = MyLogger()

#############
# Functions #
#############

def parseURL(URL):

    logger.debug("parseURL() called for URL: " + URL)

    try:
        html = urlopen(URL)

    except HTTPError as e:
        logger.error("HTTPError - Opening URL failed. Error code:'" + repr(e.code) + "', URL:'" + URL + "'")

    except Exception as e:
        logger.error("Exception - Other exception found:\n" + repr(e))
        return None

    else:
        try:
            return BeautifulSoup(html.read())
        except Exception as e:
            logger.error("Parsing HTML failed. Error:\n" + repr(e))
            return None


#################
# Scraping body #
#################

# Read configuration
try:
    config = Configurator()
    db = config.getDb()
    URL =  config.getURL()["startURL"]
    logger.debug("URL is set to " + URL)
except KeyError:
    logger.fatal("Unable to read configuration from '../config/config.ini'. Make sure you are running the script from 'scrapeforum' folder.")

# TODO decide if it is needed or it's too much spam
# Send notification email about start
Mailer(constants.EMAIL_TYPE_NOTIFICATION).send("Scraping started", "Scraping started for " + URL + " at " + datetime.strftime(datetime.now(), '%Y-%m-%d %H:%M:%S'))

# Connect to database
try:
    # Set up DB connection
    connectionString = config.getDbConnectionString()
    logger.debug("Trying to connect to DB with connectionString: " + connectionString)
    engine = create_engine(connectionString, echo=(db['echo'] == 'True'))

    # Create missing tables
    Batch.metadata.create_all(engine)
    LatestTopic.metadata.create_all(engine)

except:
    errorStr = "Failed to connect to database. Connection string: " + connectionString + ". Exiting!"
    logger.fatal(errorStr)
    Mailer(constants.EMAIL_TYPE_ERROR).send("Fatal error - failed to connect to DB", errorStr)
    os._exit(1)

try:
    # Set up and open a session
    conn = engine.connect()
    Session = sessionmaker(bind=engine)
    session = Session()

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
        session.add(ScrapeError(batchId=batch.id, errorType=constants.ERR_PARSE_FAILED, errorString=constants.ERR_PARSE_FAILED_STR + "URL='" + URL + "'"))
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
                # TODO: use logger
                print("****************")
                print(repr(latestRow))

                # Log parsing error in DB
                session.add(ScrapeError(batchId=batch.id, errorType=constants.ERR_LATEST_TOPIC_FAILED, errorString=constants.ERR_LATEST_TOPIC_FAILED_STR + "repr(latestRow): " + repr(latestRow)))

                raise


    # Scraping was successful, so set success flag to true
    session.query(Batch).filter_by(id=batch.id).update({"success": 1})
    # Notify in email about successful scrape
    Mailer(constants.EMAIL_TYPE_NOTIFICATION).send("Scraping ended - OK", "Scraping ended for " + URL + " at " + datetime.strftime(datetime.now(), '%Y-%m-%d %H:%M:%S'))

except:
    # Notify in email about failed scrape
    logger.critical("Something went wrong during scraping")

finally:
    # Send failure email notification
    # TODO: add log to email as attachment
    if logger.isErrorIndicated() == True : Mailer(constants.EMAIL_TYPE_ERROR).send("Scraping incomplete", "There was/were error(s) during scraping. Please look at attached log file.", session=session, batch_id=batch.id)

    # Close the Batch in the DB
    session.query(Batch).filter_by(id=batch.id).update({"scriptEndTime": strftime("%Y-%m-%d %H:%M:%S", gmtime())})
    session.commit()

    # Close and clean up connections
    conn.close()
    engine.dispose()



