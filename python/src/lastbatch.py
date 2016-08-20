from latesttopic import LatestTopic
from configurator import Configurator

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import func


class LastBatch(object):

    def __init__(self):
        try:
            # TODO: refactor - same code is in scrapeforum, move out to a DB object
            config = Configurator()
            db = config.getDb()

            connectionString = config.getDbConnectionString()
            engine = create_engine(connectionString, echo=(db['echo'] == 'True'))
            Session = sessionmaker(bind=engine)
            session = Session()
            # TODO - end

            self.batch_id = session.query(func.max(LatestTopic.batch_id).label("max_batch_id")).one().max_batch_id
        except:
            # TODO: report error
            raise
        finally:
            engine.dispose()

    def getProcessedSet(self):

        # TODO: refactor - same code is in scrapeforum, move out to a DB object
        config = Configurator()
        db = config.getDb()

        connectionString = config.getDbConnectionString()
        engine = create_engine(connectionString, echo=(db['echo'] == 'True'))
        Session = sessionmaker(bind=engine)
        session = Session()
        # TODO - end

        return session.query(LatestTopic).filter_by(batch_id=self.batch_id)


