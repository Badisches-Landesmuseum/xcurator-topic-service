from datetime import datetime
from typing import List, Optional

from pydantic import Field

from models.detection_status import DetectionStatus
from models.mongo_model import MongoModel
from models.topic_collection import TopicCollection, TopicTrio
from models.topic_result import TopicResult, TopTopicResult


class DocumentObject(MongoModel):
    id: Optional[str] = None
    text_list: Optional[List[str]] = None
    project_id: str = 'null'
    document_id: str = None
    upload_time: Optional[datetime] = None
    status: DetectionStatus = Field(DetectionStatus.NOT_STARTED)
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    pages_list: Optional[List] = None
    document_prediction: Optional[TopicResult] = None
    document_str: Optional[str] = None

    detected_topics_results: Optional[List] = None
    detected_topics: Optional[TopicResult] = None
    paragraphs_len: Optional[List[int]] = None
    paragraphs: Optional[List[str]] = None
    predictions_strings: Optional[List[str]] = None
    predictions_strings_accumulated_doc: Optional[List[str]] = None
    topic_document_extracted: Optional[List] = None
    accumulated_topic_document_extracted: Optional[List] = None
    topic_filtered: Optional[List] = None
    topic_document_filtered_accumulated: Optional[List] = None
    document_topic_filtered: Optional[List] = None
    page_id_list: Optional[List] = None

    class Config:
        allow_population_by_alias = True

class DokumentObjectGraphql(MongoModel):

    page_id: Optional[str] = None
    topics: Optional[List[TopicTrio]]
    #top_topics: Optional[List[List[str]]]
    status: DetectionStatus = Field(DetectionStatus.NOT_STARTED)
    #cluster_id: Optional[str] = None

    class Config:
        arbitrary_types_allowed = True
        allow_population_by_alias = True




