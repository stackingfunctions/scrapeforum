from sqlalchemy import Table, Column, Integer, String, MetaData, ForeignKey, DateTime, Sequence
from datetime import datetime
from locale import setlocale, LC_TIME

class LatestTopic(object):
    def __init__(self, latestRow):
        latestRowTableData = latestRow.findAll("td")
        self.numOfReplies = latestRowTableData[0].find("strong").getText()
        topic = latestRowTableData[2].findAll("div")[0].a
        self.topicLinkInternal = topic.attrs['href']
        self.topicTitle = topic.getText()
        category = latestRowTableData[2].findAll("div")[1].span.a
        self.categoryLinkInternal = category.attrs['href']
        self.categoryTitle = category.getText()
        topicCreated = latestRowTableData[2].findAll("div")[2].findAll("span")
        self.topicCreatedAt = topicCreated[0].attrs["title"]
        topicCreatedBy = topicCreated[1].a
        self.topicCreatedByProfileLinkExternal = topicCreatedBy.attrs['href']
        self.topicCreatedByName = topicCreatedBy.getText()

        self.numOfVisits = latestRowTableData[3].findAll("span")[0].getText()


    def display(self):
        print("\nLatest Topic:\n")
        print("num of replies: " + self.numOfReplies + "\n")
        print("topic link internal: " + self.topicLinkInternal + "\n")
        print("topic title: " + self.topicTitle + "\n")
        print("category link internal: " + self.categoryLinkInternal + "\n")
        print("category title: " + self.categoryTitle + "\n")
        print("topic created at: " + self.topicCreatedAt + "\n")
        print("topic created by link external: " + self.topicCreatedByProfileLinkExternal + "\n")
        print("topic created by name: " + self.topicCreatedByName + "\n")
        print("num of visits: " + self.numOfVisits + "\n")

    def insert2db(self, conn):
        metadata = MetaData()
        latesttopic = Table('latesttopics', metadata,
                            Column('id', Integer, Sequence('latesttopics_id_seq'), primary_key=True),
                            Column('numOfReplies', Integer),
                            Column('topicLinkInternal', String(2000)),
                            Column('topicTitle', String(255)),
                            Column('categoryLinkInternal', String(2000)),
                            Column('categoryTitle', String(255)),
                            Column('topicCreatedAt', DateTime),
                            Column('topicCreatedByProfileLinkExternal', String(2000)),
                            Column('topicCreatedByName', String(255)),
                            Column('numOfVisits', String(10)))

        # metadata.create_all(engine)
        setlocale(LC_TIME, ['hu_HU','UTF-8'])
        ins = latesttopic.insert().values(numOfReplies=self.numOfReplies,
                                          topicLinkInternal=self.topicLinkInternal,
                                          topicTitle=self.topicTitle,
                                          categoryLinkInternal=self.categoryLinkInternal,
                                          categoryTitle=self.categoryTitle,
                                          topicCreatedAt=datetime.strptime(self.topicCreatedAt, '%Y %b. %d  %H:%M'),
                                          topicCreatedByProfileLinkExternal=self.topicCreatedByProfileLinkExternal,
                                          topicCreatedByName=self.topicCreatedByName,
                                          numOfVisits=self.numOfVisits)
        result = conn.execute(ins)

        return result