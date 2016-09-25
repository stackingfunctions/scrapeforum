from sqlalchemy import Column, Integer, String, DateTime, Sequence, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

# Parent - one
class Batch(Base):
    __tablename__ = 'meta_batch'

    id = Column(Integer, Sequence('batch_id_seq'), primary_key=True)
    scriptName = Column(String(255))
    scriptStartTime = Column(DateTime(timezone=True), default=func.now())
    scriptEndTime = Column(DateTime(timezone=True))
    success = Column(Integer, default = 0)
    scrapeErrors = relationship("ScrapeError")

# Child - many
class ScrapeError(Base):

    __tablename__ = 'err_scrapeerror'

    id = Column(Integer, Sequence('scrapeerror_id_seq'), primary_key=True)
    errorType = Column(Integer)
    errorString = Column(String(2000))
    errorTime = Column(DateTime(timezone=True), default=func.now())
    batchId = Column(Integer, ForeignKey('meta_batch.id'))
    batch = relationship("Batch")

