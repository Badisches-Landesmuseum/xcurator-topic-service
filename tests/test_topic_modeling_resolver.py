import unittest
from unittest import TestCase
import logging
import os
import sys
from py_config.application_config import YamlConfig
from data_processing.data_matrix import DataMatrix
from data_processing.preprocessing.text_preprocessing import TextPreprocessing
from data_processing.handlers.text_handler import TextHandler
from py_config.application_config import YamlConfig
from data_processing.prediction_process import PredictionProcessClass
from models.xgboost import Xgboost
from models.lda import LDAModel
from data_processing.handlers.vector_handler import VectorHandler
from repositories.PickelRepository import PickelRepository
from infrastructure.rabbitmq import RabbitMQ
from rabbitmq_proto_lib.manager import RabbitManager
from repositories.PickelRepository import PickelRepository
from resolvers.topic_modeling_resolver import TopicModelingResolver
from models.topic_collection import TopicCollection
from models.topic import Topic
from infrastructure.mongo_db import MongoDB
from infrastructure.model_setup import ModelSetup
from repositories.detection_result_repository import DetectionResultRepository


from resolvers.topic_modeling_resolver import TopicModelingResolver


class TestTopicModelingResolver(TestCase):

    def test_get_page_topic_results(self):
        resolver, mongodb, topic_model,repository = TestTopicModelingResolver.setup_mongo(self)

        print(resolver)
        res = TopicModelingResolver(topic_model, repository)
        print(res.mongo)

        #self.id = '122'

        res = resolver.get_page_topic_results(info='')

        print(res)

        self.assertTrue(True)




    def setup_mongo(self):
        logging.basicConfig(level=logging.INFO)
        app_config = YamlConfig.load('.//resources/application.yml')
        model_setup = ModelSetup(app_config)
        topic_model = model_setup.creat_topic_model()

        mongodb = MongoDB(app_config['mongodb'])
        mongodb.connect()

        repository = TopicModelingResolver(mongodb, app_config['modell']['collection'])
        resolver = TopicModelingResolver(topic_model, repository)
        #detection_listener = TopicRabbitListener(topic_model, repository, app_config['modell']['project_id'])
        return resolver, mongodb, topic_model, repository