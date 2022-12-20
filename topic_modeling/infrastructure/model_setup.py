import logging

from data_processing.data_matrix import DataMatrix
from data_processing.handlers.text_handler import TextHandler
from data_processing.handlers.vector_handler import VectorHandler
from data_processing.prediction_process import PredictionProcessClass

from infrastructure.ai_model_repository import AIModelRepository
from models.lda import LDAModel
from models.xgboost import Xgboost
from repositories.GensimModelRepository import GensimModelRepository, GensimModelChooser
from repositories.PickelRepository import PickelRepository


class ModelSetup:

    def __init__(self, app_config):
        self.app_config = app_config
        self.model_name = app_config['modell']['modell_name']
        self.model_nexus_name = app_config['modell']['modell_nexus_name']
        self.model_path = '/resources/models/' + self.model_name
        self.model_path_conf = '/resources/models/' + self.model_name+'-conf'
        logging.info('AI_model_downloaded: '+ str(self.model_nexus_name) + ' ' + str(app_config['modell']['version']))

    def creat_topic_model(self):
        text_handler = TextHandler(self.app_config['modell']['language'])
        pickle_repository = PickelRepository(self.model_path_conf)
        data_matrix = DataMatrix(pickle_repository)
        prediction_model = LDAModel(self.model_path, self.model_nexus_name)
        xgboost = Xgboost(self.model_path_conf)
        nlp = text_handler._nlp
        vector_handler = VectorHandler(prediction_model, pickle_repository, xgboost)
        topic_model = PredictionProcessClass(text_handler=text_handler, vector_handler=vector_handler
                                             , data_matrix=data_matrix, prediction_model=prediction_model,
                                             model_path=self.model_path_conf, nlp=nlp)
        return topic_model
