from unittest import TestCase
from messaging.detection_listener import TopicRabbitListener
from data_processing.data_matrix import DataMatrix
from data_processing.preprocessing.text_preprocessing import TextPreprocessing
from data_processing.handlers.text_handler import TextHandler
from py_config.application_config import YamlConfig
from data_processing.prediction_process import PredictionProcessClass
from models.xgboost import Xgboost
from models.lda import LDAModel
from data_processing.handlers.vector_handler import VectorHandler
from repositories.PickelRepository import PickelRepository
#from database.detection_result_repository import DetectionResultRepository
from infrastructure.mongo_db import MongoDB
from infrastructure.rabbitmq import RabbitMQ

from data_processing.prediction_process import PredictionProcessClass

from repositories.detection_result_repository import DetectionResultRepository


class TestMongoDB(TestCase):
    def test_delete(self):
        mongo_service = TestMongoDB.setup_mongo(self)
        #project_id = '5f6383b552011079f42cfcce'
        #document_id = '6049df7fe079dc21cc97b483'

        #deletion_result = mongo_service.delete_entries_by_document(project_id, document_id)
        #deletion_result = mongo_service.delete_entries_by_document(project_id)

        #self.assertTrue(deletion_result)

        deletion_result = mongo_service.delete_entries_by_document('', '')
        self.assertTrue(not deletion_result)

    def test_get_document_topics(self):

        mongo_service = TestMongoDB.setup_mongo(self)

        document_id = '606f21e3819a3d08852e3407'
        project_id = '606ee5bf6769f83e24dc16cc'

        pages_topics, document_topics, document_topics_filtered, predefined_topic_document_filtered, paragraph_len, \
        topic_document_filtered_accumulated, page_id_list = PredictionProcessResolver._mongo.get_document_topics(ID,
                                                                                                                 project_id)


        pos = [[0, 199], [199, 200], [200, 392]]
        fil = [[0, [[['mitglied', 'landtag', 'biografie'], ['deutschland', 'ddr', 'forschung']], [], [['journal', 'europe', 'studies'], ['jude', 'aufnahme', 'archiv'], ['eu', 'migranten', 'migration']]]], [1, [[['mitglied', 'landtag', 'biografie'], ['deutschland', 'ddr', 'forschung']], [], [['journal', 'europe', 'studies'], ['jude', 'aufnahme', 'archiv'], ['eu', 'migranten', 'migration']]]]]
        acc = [[['mitglied', 'landtag', 'biografie'], ['jude', 'aufnahme', 'archiv'], ['eu', 'migranten', 'migration'], ['journal', 'europe', 'studies'], ['deutschland', 'ddr', 'forschung']], [['mitglied', 'landtag', 'biografie'], ['jude', 'aufnahme', 'archiv'], ['eu', 'migranten', 'migration'], ['journal', 'europe', 'studies'], ['deutschland', 'ddr', 'forschung']]]
        print('document_topics_filtered')
        print(document_topics_filtered)

        self.assertTrue(len(pages_topics) > 0)
        #self.assertTrue(document_topics_filtered[0] == fil)
        #self.assertTrue(paragraph_len[0][0] == pos)
        #self.assertTrue(topic_document_filtered_accumulated == acc)

    def setup_mongo(self):
        app_config = YamlConfig.load()
        model_path = '/topic_modeling/resources/models/bpb-topic-modeling'
        #nlp = TextPreprocessing.load_language_model('de_core_news_md')
        #text_handler = TextHandler(nlp)
        #pickle_repository = PickelRepository(model_path)
        #data_matrix = DataMatrix(pickle_repository)
        #prediction_model = LDAModel(model_path)
        #xgboost = Xgboost(model_path)
        mongodb = MongoDB(app_config['mongodb'])
        mongodb.connect()

        repository = DetectionResultRepository(mongodb, app_config['modell']['collection'])


        #vector_handler = VectorHandler(prediction_model, pickle_repository, xgboost)
        #topic_model = PredictionProcessClass(text_handler=text_handler, vector_handler=vector_handler
        #                              , data_matrix=data_matrix, prediction_model=prediction_model, nlp=nlp,
        #                              model_path=model_path)
        #rabbitmq = RabbitMQ(app_config['rabbitmq'])
        #rabbit_service = TopicRabbitListener(url=rabbitmq.amqp_url, service=topic_model, mongodb=repository)



        '''model_path_conf = '/topic_modeling/resources/models/bpb-topic-modeling-conf'
        model_path = '/topic_modeling/resources/models/bpb-topic-modeling'
        model_nexus_name = 'lda_wraped.gensim'#'lda_model_mal'
        text_handler = TextHandler('DE')
        pickle_repository = PickelRepository(model_path_conf)
        print(pickle_repository)
        data_matrix = DataMatrix(pickle_repository)
        prediction_model = LDAModel(model_path, model_nexus_name)
        xgboost = Xgboost(model_path_conf)
        vector_handler = VectorHandler(prediction_model, pickle_repository, xgboost)
        nlp = text_handler._nlp
        print(nlp)
        topic_model = PredictionProcessClass(text_handler=text_handler, vector_handler=vector_handler
                                             , data_matrix=data_matrix, prediction_model=prediction_model,
                                             model_path=model_path_conf,nlp=nlp)'''
        return repository


