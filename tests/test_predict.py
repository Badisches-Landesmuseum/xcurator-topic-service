from unittest import TestCase

from data_processing.data_matrix import DataMatrix
from data_processing.preprocessing.text_preprocessing import TextPreprocessing
from data_processing.handlers.text_handler import TextHandler
from py_config.application_config import YamlConfig
from data_processing.prediction_process import PredictionProcessClass
from models.xgboost import Xgboost
from models.lda import LDAModel
from data_processing.handlers.vector_handler import VectorHandler
from repositories.PickelRepository import PickelRepository
from datetime import datetime
from typing import List, Optional
from repositories.GensimModelRepository import GensimModelRepository, GensimModelChooser
from repositories.PickelRepository import PickelRepository

from pydantic import Field
#from datamodels.document_object import DocumentObject

from bson import ObjectId
from pydantic import BaseModel, BaseConfig, Field
from models.detection_status import DetectionStatus
from models.mongo_model import MongoModel
from models.topicresult import TopicResult

class DocumentObject(MongoModel):
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

class TestPredictionClass(TestCase):
    def test_execute_documents(self):

        topic_model = TestPredictionClass.setup_tm(self)
        text_list_p = DocumentObject(text_list = ['<p> deutete nichts Gutes. Wer würde ihm schon folgen, säpt in der Nacht und dazu noch in dieser engen Gasse mitten im übel beleum undeten Hafenviertel? Gerade jetzt, wo er das Ding seines Lebens gedreht </p> </p> hatte und mit der Beute verschwinden wollte! Hatte einer seiner zahllosen Kollegen dieselbe Idee gehabt, ihn beobachtet und abgewartet, um ihn nun um die Früchte seiner Arbeit zu erleichtern?'])
        text_list_b = DocumentObject(text_list = ['<p> deutete nichts Gutes. Wer würde ihm schon folgen, säpt in der Nacht und dazu noch in dieser engen Gasse mitten im übel beleum undeten Hafenviertel? Gerade jetzt, wo er das Ding seines Lebens gedreht <br> <br> hatte und mit der Beute verschwinden wollte! Hatte einer seiner zahllosen Kollegen dieselbe Idee gehabt, ihn beobachtet und abgewartet, um ihn nun um die Früchte seiner Arbeit zu erleichtern?'])

        document_object = topic_model.execute_documents(document_object = text_list_p, xgboost_flag=True, acumulated_text=True)
        document_object_b = topic_model.execute_documents(document_object = text_list_b, xgboost_flag=True, acumulated_text=True)
        self.assertTrue(len(document_object.pages_list[0])==3)
        self.assertEqual(type(document_object.pages_list[0][1][0]), str)
        self.assertTrue(len(document_object_b.pages_list[0]) == 3)
        self.assertEqual(type(document_object_b.pages_list[0][1][0]), str)


    def setup_tm(self):
        model_path_conf = '/topic_modeling/resources/models/bpb-topic-modeling-conf'
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
                                             model_path=model_path_conf,nlp=nlp)
        return topic_model