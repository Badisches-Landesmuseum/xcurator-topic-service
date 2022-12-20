from typing import List, Optional
from models.topic import Topic
from pydantic import BaseModel, Field
from models.detection_status import DetectionStatus

class TopicCollection(BaseModel):
    percentage: Optional[float]
    topics: Optional[List[Topic]]

class TopicTrio(BaseModel):
    top_0: str
    top_1: str
    top_2: str

class ParagraphTopicTrio(BaseModel):
    paragraph_top_0: str
    paragraph_top_1: str
    paragraph_top_2: str
    start_pos: int
    end_pos: int

class TopicDetection(BaseModel):
    #page_id: Optional[str] = None
    topicTrio: List[TopicTrio]
    paragraphTopicTrio: List[ParagraphTopicTrio]
    topicDetectionStatus: DetectionStatus = Field(DetectionStatus.NOT_STARTED)

