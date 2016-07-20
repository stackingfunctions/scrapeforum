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
        return None
