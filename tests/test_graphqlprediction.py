from unittest import TestCase

from database.detection_result_repository import MongoDB, DetectionResultRepository
from py_config.application_config import YamlConfig

from data_processing.data_matrix import DataMatrix
from data_processing.handlers.text_handler import TextHandler
from data_processing.handlers.vector_handler import VectorHandler
from data_processing.prediction_process import PredictionProcessClass
from data_processing.preprocessing.text_preprocessing import TextPreprocessing
from infrastructure.fastapi import FastAPIServer
from infrastructure.rabbitmq import RabbitMQ
from models.lda import LDAModel
from models.xgboost import Xgboost
from repositories.PickelRepository import PickelRepository
from resolvers.topic_modeling_resolver import TopicModelingResolver


class TestPredictionResolver(TestCase):

    def test_prediction_query_graphql_execute(self):
        mongo, service = TestPredictionResolver.setup_mongo(self)
        resolver = TopicModelingResolver(service=service, mongodb=mongo)
        document_id = '606ef519c156ac1df464bbce'
        project_id = '5f6383b552011079f42cfcce'
        info = ''
        result = TopicModelingResolver.prediction_query_graphql_execute(service, info='', document_id=document_id,
                                                                        project_id=project_id)

        #document_object = DocumentObject(document_id=7, project_id=77, created_at=None)
        #mongo.store(document_object)

        print('result')
        print(result)


        res = mongo.exists(project_id=project_id, document_id=document_id)
        #print('res')
        #print(res)

       # print('result')
       # print(result)
        self.assertTrue(True)

    def setup_mongo(self):
        app_config = YamlConfig.load()
        model_path = '/topic_modeling/resources/models/bpb-topic-modeling'
        nlp = TextPreprocessing.load_language_model('de_core_news_md')
        text_handler = TextHandler(nlp)
        pickle_repository = PickelRepository(model_path)
        data_matrix = DataMatrix(pickle_repository)
        prediction_model = LDAModel(model_path)
        xgboost = Xgboost(model_path)

        mongodb = MongoDB(app_config['mongo'])
        mongodb.connect()

        repository = DetectionResultRepository(mongodb, 'topic_modeling_collection')

        vector_handler = VectorHandler(prediction_model, pickle_repository, xgboost)
        topic_model = PredictionProcessClass(text_handler=text_handler, vector_handler=vector_handler
                                             , data_matrix=data_matrix, prediction_model=prediction_model, nlp=nlp,
                                             model_path=model_path)
        rabbitmq = RabbitMQ(app_config['rabbitmq'])
       # rabbit_service = TopicRabbitListener(url=rabbitmq.amqp_url, service=topic_model, mongodb=repository)
        rabbitmq = RabbitMQ(app_config['rabbitmq'])
        # logging.info(app_config['rabbitmq'])
        #rabbit_service = TopicRabbitListener(url=rabbitmq.amqp_url, service=topic_model, mongodb=repository)
        webserver = FastAPIServer(app_config['server'])

        # thread = threading.Thread(target=rabbit_service.run)
        # thread.setDaemon(True)
        # thread.start()
        # webserver.start(topic_model, mongodb)
        return repository, topic_model


    def test_prediction_query_graphql_execute_1(self):
        mongodb, service = TestPredictionResolver.setup_mongo(self)
        text = '<p>Sie hätten noch ins Boot springen können, aber der Reisende hob ein schweres, geknotetes Tau  vom Boden, drohte ihnen damit und hielt sie dadurch von dem Sprunge ab. In den letzten Jahrzehnten ist das Interesse an Hungerkünstlern sehr zurückgegangen. Aber sie überwanden sich, umdrängten den Käfig und wollten sich gar nicht fortrühren. Jemand musste Josef K. verleumdet haben, denn ohne dass er etwas Böses getan hätte, wurde er eines Morgens verhaftet. »Wie ein Hund! </p> <p>« sagte er, es war, als sollte die Scham ihn überleben. Als Gregor Samsa eines Morgens aus unruhigen Träumen erwachte, fand er sich in seinem Bett zu einem ungeheueren Ungeziefer verwandelt. Und es war ihnen wie eine Bestätigung ihrer neuen Träume und guten Absichten, als am Ziele ihrer Fahrt die Tochter als erste sich erhob und ihren jungen Körper dehnte.</p>'
        document_id = '222'
        project_id = '333'
        info = ''
        result = TopicModelingResolver.prediction_query_graphql_execute_1(service, info='', text = text)
        print('result')
        print(result)
        self.assertTrue(True)
