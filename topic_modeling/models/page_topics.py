from proto.dreipc.asset.topicmodeling import PageTopicsProto


class PageTopics:
    page_id: str
    topics: [str]

    def __init__(self, page_id: str, topics: [str]):
        self.page_id= page_id
        self.topics = topics

    def proto(self):
        return PageTopicsProto(
            page_id=self.page_id,
            topics=self.topics
        )
