from sqlalchemy import Table, Column, Integer, String, DateTime, Sequence
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
from locale import setlocale, LC_TIME

Base = declarative_base()

class LatestTopic(Base):

    __tablename__ = 'scr_latesttopics'

    id = Column(Integer, Sequence('latesttopics_id_seq'), primary_key=True)
    numOfReplies = Column(Integer)
    topicLinkInternal = Column(String(2000))
    topicTitle = Column(String(255))
    categoryLinkInternal = Column(String(2000))
    categoryTitle = Column(String(255))
    topicCreatedAt = Column(DateTime)
    topicCreatedByProfileLinkExternal = Column(String(2000))
    topicCreatedByName = Column(String(255))
    numOfVisits = Column(String(10))

    def __init__(self, latestRow):
        # set the local for date parsing
        setlocale(LC_TIME, ['hu_HU','UTF-8'])

        latestRowTableData = latestRow.findAll("td")
        self.numOfReplies = latestRowTableData[0].find("strong").getText()
        topic = latestRowTableData[2].findAll("div")[0].a
        self.topicLinkInternal = topic.attrs['href']
        self.topicTitle = topic.getText()
        category = latestRowTableData[2].findAll("div")[1].span.a
        self.categoryLinkInternal = category.attrs['href']
        self.categoryTitle = category.getText()
        topicCreated = latestRowTableData[2].findAll("div")[2].findAll("span")
        self.topicCreatedAt = datetime.strptime(topicCreated[0].attrs["title"], '%Y %b. %d  %H:%M')
        topicCreatedBy = topicCreated[1].a
        self.topicCreatedByProfileLinkExternal = topicCreatedBy.attrs['href']
        self.topicCreatedByName = topicCreatedBy.getText()

        self.numOfVisits = latestRowTableData[3].findAll("span")[0].getText()


    def __repr__(self):
        return "<LatestTopic(id='%s', numOfReplies='%s', topicLinkInternal='%s' topicTitle='%s', categoryLinkInternal='%s', categoryTitle='%s', topicCreatedAt='%s', topicCreatedByProfileLinkExternal='%s', topicCreatedByName='%s', numOfVisits='%s')>" % \
               (self.id, self.numOfReplies, self.topicLinkInternal, self.topicTitle, self.categoryLinkInternal, self.categoryTitle, self.topicCreatedAt, self.topicCreatedByProfileLinkExternal, self.topicCreatedByName, self.numOfVisits)
