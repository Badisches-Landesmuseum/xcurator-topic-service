import logging
from ariadne import QueryType
from ariadne_extensions import federation
from pydantic import BaseModel, Field
from typing import List, Optional
from py_config.application_config import YamlConfig
from infrastructure.mongo_db import MongoDB

from data_processing.prediction_process import PredictionProcessClass
from models.detection_status import DetectionStatus
from models.document_object import DokumentObjectGraphql
from models.page_object import PageObjectGraphql
from repositories.detection_result_repository import DetectionResultRepository
from resolvers.resolver import GraphQLResolver
from models.topic_result import TopicResult, TopTopicResult
from models.topic_collection import TopicCollection, TopicTrio, ParagraphTopicTrio
from models.topic_collection import TopicDetection


'''
pydantic Model representing the corresponding type in the schema definition
'''


class Document(BaseModel):
    page_id: Optional[str] = None
    topics: Optional[List[TopicTrio]]
    # top_topics: Optional[List[List[str]]]
    status: DetectionStatus = Field(DetectionStatus.NOT_STARTED)
    # cluster_id: Optional[str] = None


class Page(BaseModel):
    topicDetection: TopicDetection


#class TopicDetection(BaseModel):
    #page_id: Optional[str] = None
 #   topicTrio: list #List[TopicTrio]
  #  paragraphTopicTrio: list #List[ParagraphTopicTrio]
   # topicDetectionStatus: DetectionStatus = Field(DetectionStatus.NOT_STARTED)

    #topicTrio: Optional[list]
    #topicDetectionStatus: DetectionStatus = Field(DetectionStatus.NOT_STARTED)
    #paragraphTopicTrio: Optional[list]



class TopicModelingResolver(GraphQLResolver):
    document_prediction_query = QueryType()
    page_prediction_query = QueryType()
    page_type = federation.FederatedObjectType("Page")
    page_type.set_alias('topicDetection', 'topicDetection')

    document_type = federation.FederatedObjectType("Document")
    document_type.set_alias('topicDetectionStatus', "topicDetectionStatus")

    detection_type = federation.FederatedObjectType("TopicDetection")
    detection_type.set_alias('topicDetectionStatus', "topicDetectionStatus")
    detection_type.set_alias('topicTrio', "topicTrio")
    detection_type.set_alias('paragraphTopicTrio', "paragraphTopicTrio")

    paragraph_topic_trio = federation.FederatedObjectType("ParagraphTopicTrio")

    overall_service = None
    _mongo = None

    def __init__(self, service: PredictionProcessClass, mongodb: DetectionResultRepository):
        super(TopicModelingResolver, self).__init__()
        TopicModelingResolver.overall_service = service
        TopicModelingResolver._mongo = mongodb

    # TODO: delete
    @page_prediction_query.field('detectPageIDTopics')
    def prediction_query_graphql_execute_page(self, info, **kwargs):
        page_id = kwargs.get("page_id")
        try:
            page_paragraph_topics = TopicModelingResolver._mongo.get_page_paragraph_top_topics(page_id)

            page_topic_results = TopicDetection(topicTrio=TopicModelingResolver._mongo.get_page_top_topics(page_id),
                                                   paragraphTopicTrio=page_paragraph_topics,
                                                   topicDetectionStatus=DetectionStatus.DONE)

            print(page_topic_results)
            return page_topic_results.dict()


        except Exception as e:
            logging.info(e)
            return PageObjectGraphql(topicTrio=[], paragraphTopicTrio=[], topicDetectionStatus=DetectionStatus.ERROR).dict()

    @document_type.field('topicTrio')
    def get_document_topic_results(self, info, **kwargs) -> DokumentObjectGraphql:
        document_id = kwargs.get("document_id")
        logging.info(document_id)
        try:
            return Document(topics=TopicModelingResolver._mongo.get_document_top_topics(document_id),
                                         topicDetectionStatus=DetectionStatus.DONE).dict()
        except Exception as e:
            logging.info(e)
            return Document(topics=[], topicDetectionStatus=DetectionStatus.ERROR).dict()

    @page_type.field('topicDetection')
    def get_page_topic_results(self, info, **kwargs):
        page_id = str(self["id"])
        try:
            page_paragraph_topics = TopicModelingResolver._mongo.get_page_paragraph_top_topics(page_id)

            #TopicDetection
            page_topic_results = TopicDetection(topicTrio=TopicModelingResolver._mongo.get_page_top_topics(page_id),
                              paragraphTopicTrio=page_paragraph_topics,
                              topicDetectionStatus=DetectionStatus.DONE)

            print(page_topic_results)

            return page_topic_results.dict()

        except Exception as e:
            logging.info(e)
            return TopicDetection(topicTrio=[], paragraphTopicTrio=[], topicDetectionStatus=DetectionStatus.ERROR).dict()

    def get_schemas(self) -> List:
        return [self.page_type, self.document_type, self.page_prediction_query, self.detection_type] #self.page_topic_results_type,
        '''[self.prediction_type, self.document_prediction_query, self.page_prediction_query]'''
