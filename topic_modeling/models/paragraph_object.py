from typing import List, Optional

from pydantic import BaseModel

from models.mongo_model import MongoModel
from models.topic_result import TopicResult, TopTopicResult


class ParagraphObject(MongoModel):

    position: Optional[List[int]] = [0,0]
    topics: Optional[List[TopicResult]]
    top_topics: Optional[List[TopTopicResult]]

    class Config:
        arbitrary_types_allowed = True
        allow_population_by_alias = True




