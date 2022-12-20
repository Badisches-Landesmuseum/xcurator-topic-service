import logging
import warnings
from typing import List

from data_processing.data_matrix import DataMatrix
from data_processing.handlers.text_handler import TextHandler
from data_processing.handlers.vector_handler import VectorHandler
from data_processing.output_generation import OutputGeneration
from models.document_object import DocumentObject
from models.lda import LDAModel
from models.topic_result import TopicResult
from repositories.GensimModelRepository import GensimModelRepository
from repositories.PickelRepository import PickelRepository
from repositories.PickelRepository import PickelTypeChooser

warnings.filterwarnings("ignore", category=FutureWarning)
logging.basicConfig(level=logging.INFO, format='%(message)s')


class PredictionProcessClass:
    text = 'Empty'
    clean_text = 'Empty'

    def __init__(self, text_handler: TextHandler, vector_handler: VectorHandler, data_matrix: DataMatrix,
                 prediction_model: LDAModel, model_path, nlp) -> None:
        self.text = PredictionProcessClass.text
        self._clean_text = PredictionProcessClass.clean_text
        self._topics = PickelRepository.get(PickelRepository(model_path), PickelTypeChooser.Topics)
        self.text_handler = text_handler
        self.vector_handler = vector_handler
        self.data_matrix = data_matrix
        self.prediction_model = prediction_model
        self._nlp = nlp

    def _prepare_text_to_paragraph(self, text: str = None) -> List[str]:
        try:
            paragraphs, paragraphs_positions = self.text_handler.split_into_paragraphs(text)
            paragraphs = self.text_handler.clean_text(paragraphs)
            if len(paragraphs) == 0 or (len(paragraphs[0].split(' ')) <= 2 and len(paragraphs) == 0):
                logging.info("Logged Error: Not enough text given in paragraphs!")
        except Exception as e:
            logging.error("Error during text preperation: " + str(e))
            paragraphs = []
            paragraphs_positions = []
        return paragraphs, paragraphs_positions

    def _prepare_text(self, text: str = None) -> List[str]:
        try:
            text_cleaned = self.text_handler.clean_text([text])
            paragraphs_positions = [0, len(text)]
            if len(text_cleaned) == 0 or (len(text_cleaned[0].split(' ')) <= 3):
                logging.info("Logged Error: Not enough text given in paragraphs!")
                paragraphs_positions = []
                text_cleaned = []
        except Exception as e:
            logging.error("Error during text preperation: " + str(e))
            paragraphs_positions = []
        return text_cleaned, paragraphs_positions

    def execute(self, text: str, acumulated_text: bool = False, xgboost_flag: bool = True, paragraph_flag: bool = True) -> [TopicResult, List]:
        #try:
        OutputGeneration.text_empty_test(self, text)
        if paragraph_flag:
            paragraphs, paragraphs_positions = self._prepare_text_to_paragraph(text)
            if acumulated_text:
                paragraphs.append(' '.join(paragraphs))
            paragraph_matrices = [self.data_matrix.create(text) for text in paragraphs]
            merged_paragraph_matrices = [self.data_matrix.merge_to_superset_matrix(data) for data in
                                         paragraph_matrices]
            paragraph_topics = [self.prediction_model.predict(dataframe) for dataframe in merged_paragraph_matrices]
            paragraph_topics_cleaned = [self.vector_handler.clean_lda_results(topic[0]) for topic in
                                        paragraph_topics]
            xgboost_results = []
            if xgboost_flag:
                xgboost_results = [self.vector_handler.execute_xgboost_prediction(topic[1]) for topic in
                                   paragraph_topics]
        else:
            text, paragraphs_positions = self._prepare_text(text)
            paragraphs = text
            if len(text) != 0:
                paragraph_matrix = self.data_matrix.create(text[0])
                merged_paragraph_matrices = self.data_matrix.merge_to_superset_matrix(paragraph_matrix)
                paragraph_topics = self.prediction_model.predict(merged_paragraph_matrices)
                paragraph_topics_cleaned = [self.vector_handler.clean_lda_results(paragraph_topics[0])]
            else:
                paragraph_topics_cleaned = []
            xgboost_results = []
            if xgboost_flag:
                xgboost_results = self.vector_handler.execute_xgboost_prediction(paragraph_topics[1])

        result_set = OutputGeneration.make_result_set(self, paragraph_topics_cleaned=paragraph_topics_cleaned,
                                                      xgboost_results=xgboost_results, deleted_indexes=[],
                                                      xgboost_flag=xgboost_flag)

        topic_result = TopicResult(results=result_set)
        #except Exception as e:
         #   logging.error("Error during document execution : " + str(e))
          #  paragraphs = ['none']
           # topic_result = TopicResult(results=[0.0, ['']])
            #paragraphs_positions = [0, 0]

        return topic_result, paragraphs, paragraphs_positions

    def prepare_results_to_output(self, topic_results: List[TopicResult], paragraphs: List[str],
                                  acumulated_text: bool = False,
                                  xgboost_flag: bool = False, string_representation: bool = True) -> TopicResult:
        vectors = [self.text_handler.to_vectors(text) for text in paragraphs]
        middle_points = [self.vector_handler.average_2d(vector) for vector in vectors]
        word_collection = []
        for topic in topic_results:
            collection = []
            index_correction = 0
            for index, topics in enumerate(topic.results):
                if topics != []:
                    collection.append(OutputGeneration.find_words_inpotic_closest_to_input(self, topics[0],
                                                                                           middle_points[
                                                                                               index - index_correction],
                                                                                           self.vector_handler))
                else:
                    collection.append([])
                    index_correction += 1
            word_collection.append(collection)
        if string_representation:
            out_topic_string = OutputGeneration.make_topic_output_string(self, word_collection, acumulated_text)
        else:
            out_topic_string = OutputGeneration.make_topic_output_list(self, word_collection, acumulated_text)
        if xgboost_flag:
            output_xgboost_string = []
            for topic in topic_results:
                string = []
                for top in topic.results:
                    if topic != [] and top != []:
                        string.append(OutputGeneration.make_classification_output_string(self, top))
                    else:
                        string.append([])

                output_xgboost_string.append(string)
            result_set = [[out_topic_string, output_xgboost_string[len(output_xgboost_string) - 1]]]
        else:
            result_set = [[out_topic_string, 'Xgboost prediction disabled.']]
        topic_result_result_set = TopicResult(results=result_set)
        return topic_result_result_set

    def execute_documents(self, document_object: DocumentObject, acumulated_text: bool = False,
                          xgboost_flag: bool = True, paragraph_flag: bool = True) -> DocumentObject:
        documents = document_object.text_list
        if documents is None or len(documents) == 0:
            raise ValueError("Error: No document given!")
        pages_list = [self.execute(text=document, acumulated_text=acumulated_text, xgboost_flag=xgboost_flag, paragraph_flag = paragraph_flag) for
                      document in documents]

        document_str = ''
        for tupel in pages_list:
            if len(tupel[1]) >= 1:
                document_str = document_str + (' '.join(tupel[1]))
        document_prediction = self.execute(document_str, acumulated_text, xgboost_flag, paragraph_flag)
        document_object.pages_list = pages_list
        document_object.document_prediction = document_prediction
        document_object.document_str = document_str
        return document_object

    def start_predict_process(self):
        topic_result = self.execute(self.text)
        return topic_result.results
