from datetime import datetime
from typing import List, Optional

from pydantic import Field

from models.detection_status import DetectionStatus
from models.mongo_model import MongoModel
from models.page_object import PageObject
from models.topic_result import TopicResult, TopTopicResult


class MongoDBObject(MongoModel):
    id: Optional[str] = None
    project_id: str = 'null'
    document_id: str = None
    upload_time: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    status: DetectionStatus = Field(DetectionStatus.NOT_STARTED)

    pages: Optional[List[PageObject]]
    topics: Optional[List[TopicResult]]
    top_topics: Optional[List[TopTopicResult]]

    class Config:
        arbitrary_types_allowed = True
        allow_population_by_alias = True




