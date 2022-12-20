from datetime import datetime
from typing import List, Optional

from pydantic import Field, BaseModel
from models.detection_status import DetectionStatus
from models.mongo_model import MongoModel
from models.paragraph_object import ParagraphObject
from models.topic_result import TopicResult, TopTopicResult
from models.topic_collection import TopicCollection, TopicTrio, ParagraphTopicTrio


class PageObject(MongoModel):

    page_id: Optional[str] = None
    topics: Optional[List[TopicResult]]
    top_topics: Optional[List[TopTopicResult]]

    paragraphs: Optional[List[ParagraphObject]]
    cluster_id: Optional[str] = None

    class Config:
        arbitrary_types_allowed = True
        allow_population_by_alias = True


class PageObjectGraphql(BaseModel):
    page_id: Optional[str] = None
    topic_trio: Optional[List[TopicTrio]]
    paragraph_topic_trio: Optional[List[ParagraphTopicTrio]]
    topicDetectionStatus: DetectionStatus = Field(DetectionStatus.NOT_STARTED)
    cluster_id: Optional[str] = None

    class Config:
        arbitrary_types_allowed = True
        allow_population_by_alias = True



