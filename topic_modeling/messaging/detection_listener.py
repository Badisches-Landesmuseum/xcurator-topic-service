import logging
from typing import List

from rabbitmq_proto_lib.listener import RabbitListener

from data_processing.prediction_process import PredictionProcessClass
from models.detection_status import DetectionStatus
from models.document_object import DocumentObject
from models.mongodb_object import MongoDBObject
from models.page_object import PageObject
from models.page_topics import PageTopics
from models.paragraph_object import ParagraphObject
from models.topic_result import TopicResult, TopTopicResult
from proto.dreipc.asset.topicmodeling import EnrichmentStatusProto, TopicDetectionProto, TopicObjectProto, \
    PageTopicsProto
from proto.dreipc.q8r.proto.asset import DocumentProto
from repositories.detection_result_repository import DetectionResultRepository


class TopicRabbitListener(RabbitListener):

    def __init__(self, service: PredictionProcessClass, repository: DetectionResultRepository, project_id):

        self.name = 'asset.document.topic.detect'
        self.exchange_name = 'assets'
        self.routing_keys = ['document.created']
        self.dead_letter_exchange = "assets-dlx"
        self.prefetch_count = 1
        self._repository = repository
        self.service = service
        self.project_id = project_id
        self.siemens_services = []

    async def on_message(self, body: DocumentProto, message):
        if isinstance(body, str):
            return message.reject(requeue=True)
        status = DetectionStatus.PENDING

        document_object = TopicRabbitListener.create_document_object(self, body)
        if self._repository.exists(document_object.document_id):
            #document_prediction_results = self._repository.get_document_result(document_id=document_object.document_id,
             #                                                                  project_id=document_object.project_id)
            proto_objects = []
        else:
            logging.info(document_object.project_id)
            logging.info(self.project_id)
            if document_object.project_id != self.project_id and (self.project_id != '606ee5bf6769f83e24dc16cc' and
                                                                   document_object.project_id not in self.siemens_services ):
                return message.reject(requeue=True)

            logging.info(
                "Detect Document objects: Project: " + document_object.project_id + ' Doc: ' + document_object.document_id)

            try:
                #TODO: Refactor
                # Siemens spezifisch
                paragraph_flag = True
                xgboost_flag = True

                if document_object.project_id in self.siemens_services:
                    paragraph_flag = False
                    xgboost_flag = False

                document_prediction_results = self.service.execute_documents(document_object=document_object,
                                                                             xgboost_flag=xgboost_flag,
                                                                             acumulated_text=True,
                                                                             paragraph_flag=paragraph_flag)

                document_prediction_results = TopicRabbitListener.extract_results(self, document_prediction_results)

                document_prediction_results.predictions_strings = TopicRabbitListener. \
                    create_prediction_string_for_paragraphs(self, document_prediction_results.paragraphs,
                                                            document_prediction_results.detected_topics,
                                                            xgboost_flag)

                document_prediction_results.predictions_strings_accumulated_doc = TopicRabbitListener. \
                    create_prediction_string_for_paragraphs(self, [document_prediction_results.document_prediction[1]],
                                                            [document_prediction_results.document_prediction[0]],
                                                            xgboost_flag)

                status = DetectionStatus.DONE
            except Exception as e:
                logging.error("Error during topic detection: " + str(e))
                document_prediction_results = document_object
                document_prediction_results.predictions_strings = ['none']
                document_prediction_results.predictions_strings_accumulated_doc = ['none']
                status = DetectionStatus.ERROR
            try:
                document_prediction_results.topic_document_extracted = TopicRabbitListener.extract_topics(self,
                                                                                                          document_prediction_results.predictions_strings)

                document_prediction_results.accumulated_topic_document_extracted = TopicRabbitListener. \
                    extract_topics(self, document_prediction_results.predictions_strings_accumulated_doc)

                topic_filtered, topic_document_filtered_accumulated = TopicRabbitListener. \
                    seperate_accumulated(self, document_prediction_results.topic_document_extracted,
                                         document_prediction_results.page_id_list)

                document_prediction_results.topic_filtered = topic_filtered
                document_prediction_results.topic_document_filtered_accumulated = topic_document_filtered_accumulated
                document_topic_filtered, document_topic_document_filtered_accumulated = TopicRabbitListener.seperate_accumulated(
                    self, document_prediction_results.accumulated_topic_document_extracted,
                    document_prediction_results.page_id_list)

                if len(document_topic_filtered[0]) == 1:
                    document_prediction_results.document_topic_filtered = document_topic_filtered[0][0]
                else:
                    document_prediction_results.document_topic_filtered = document_topic_filtered[0][1][0]

            except Exception as e:
                logging.error("Error during topic representation: " + str(e))
                document_prediction_results.detected_topics = ['none']
                document_prediction_results.topic_filtered = ['none']
                document_prediction_results.document_topic_filtered = ['none']
                status = DetectionStatus.ERROR

            proto_objects = TopicRabbitListener.make_proto_objects(self, document_prediction_results.detected_topics)

            try:
                page_objects = []

                for page_number, page in enumerate(document_prediction_results.pages_list):

                    paragraphs_positions = page[2]
                    paragraph_objects = []
                    #minus one because the all page prediction was added last
                    for index, paragraph in enumerate(page[0].results[:-1]):
                        if index >= len(paragraphs_positions):

                            paragraph_position_index = len(paragraphs_positions) - 1
                        else:
                            paragraph_position_index = index
                        topic_results = self.get_topics_paragraph(paragraph=paragraph)
                        top_topics_pages = document_prediction_results.topic_document_extracted
                        top_topics_results = self.get_top_topics_paragraph(pages=top_topics_pages,page_number=page_number,
                                                                        paragraph_index=index)

                        paragraph_object = ParagraphObject(position=paragraphs_positions[paragraph_position_index],
                                                           topics=topic_results, top_topics=top_topics_results)

                        paragraph_objects.append(paragraph_object)


                    if paragraph_flag:
                        topics_page = self.get_topics_parapgraph_page(collection=page[0].results[-1:][0][0])
                    else:
                        topics_page = self.get_topics(collection=page[0].results[0][0])

                    top_topics_page = self.get_top_topics_page(collection=document_prediction_results.topic_document_filtered_accumulated, page_number = page_number)

                    page_object = PageObject(page_id=document_prediction_results.page_id_list[page_number],
                               paragraphs=paragraph_objects, topics=topics_page, top_topics=top_topics_page)
                    page_objects.append(page_object)

                topics_document = self.get_topics(collection=document_prediction_results.document_prediction[0].results[0][0])

                top_topics_document = self.get_top_topics_document(collection=document_prediction_results.document_topic_filtered)

                mongo_object= MongoDBObject(project_id=document_prediction_results.project_id,
                              document_id=document_prediction_results.document_id,
                              upload_time=document_prediction_results.upload_time,
                              created_at=document_prediction_results.created_at,
                              updated_at=document_prediction_results.updated_at,
                              status=status,
                              pages=page_objects,
                              topics=topics_document,
                              top_topics=top_topics_document)

            except Exception as e:
                logging.error("Error during MongoDBObject creation: " + str(e))
                status = DetectionStatus.ERROR

            try:
                self._repository.store(mongo_object)

            except Exception as e:
                logging.error("Error during mongo store: " + str(e))
                status = DetectionStatus.ERROR

        try:
            page_protos = self.create_page_topics_proto(document_prediction_results.topic_document_extracted,
                                                        document_prediction_results.page_id_list)

            proto_result = TopicDetectionProto(document_id=str(body.id),
                                               project_id=str(body.project_id),
                                               topics=proto_objects,
                                               page_topics=page_protos,
                                               status=EnrichmentStatusProto.from_string(status),
                                               provided_by='topic-modeling-service')

            await self.convert_and_send("asset.document.topic.detected", proto_result, self.exchange_name)
        except Exception as e:
            logging.error("Error during result send: " + str(e))

    def get_topics_paragraph(self, paragraph) -> [TopicResult]:
        paragraph_topics = []
        for topics in paragraph[:-1]:
            if len(topics) > 0:
                if len(topics[0]) > 0:
                    for topic in topics:
                        topic_result = TopicResult(results = [topic[0], topic[1]])
                        paragraph_topics.append(topic_result)
                else:
                    topic_result = TopicResult(results = [0.0, ['']])
                    paragraph_topics.append(topic_result)
            else:
                topic_result = TopicResult(results=[0.0, ['']])
                paragraph_topics.append(topic_result)
        return paragraph_topics

    def get_top_topics_paragraph(self, pages, page_number, paragraph_index) -> [TopTopicResult]:
        if pages is not None:
            topic = pages[page_number][1][paragraph_index]
            topic = self.nest_list(topic)
            top_topic_result = TopTopicResult(results = topic)
        else:
            top_topic_result = TopTopicResult(results= [[['']]])
        return [top_topic_result]

    def get_topics(self, collection) -> [TopicResult]:
        topics = []
        for topic in collection[:-1]:
            topic_result = TopicResult(results = [topic[0],topic[1]])
            topics.append(topic_result)
        return topics

    def get_topics_parapgraph_page(self, collection) -> [TopicResult]:
        topics = []
        for topic in collection:
            print('para_topic')
            print(topic)
            topic_result = TopicResult(results = [topic[0],topic[1]])
            topics.append(topic_result)
        return topics

    def get_top_topics_page(self, collection, page_number) -> [TopTopicResult]:
        page_top_topics = []
        if collection is not None:
            for topic in collection[page_number][0]:
                topic = self.nest_list(topic)
                top_topic_result = TopTopicResult(results = topic)
                page_top_topics.append(top_topic_result)
        else:
            page_top_topics.append(TopTopicResult(results = [[['']]]))
        return page_top_topics

    def get_top_topics_document(self, collection) -> [TopTopicResult]:
        top_topics= []
        if collection is not None and collection[0] != 'none':
            for topic in collection:

                topic = self.nest_list(topic)

                top_topic_result = TopTopicResult(results = topic)
                top_topics.append(top_topic_result)
        else:
            top_topics.append(TopTopicResult(results=[[['']]]))
        return top_topics

    def create_document_object(self, body) -> DocumentObject:
        pages_list = body.pages
        text_list = [page.html for page in pages_list]
        page_id_list = [page.id for page in pages_list]
        if len(text_list) == 0 or text_list is None:
            text_list = ['Empty']
        return DocumentObject(pages_list=pages_list, text_list=text_list, project_id=body.project_id,
                              document_id=body.id,
                              upload_time=body.uploaded_time, page_id_list=page_id_list)

    def extract_results(self, document_prediction_results) -> DocumentObject:
        document_prediction_results.detected_topics_results = [element[0].results for element in
                                                               document_prediction_results.pages_list]
        document_prediction_results.detected_topics = [element[0] for element in
                                                       document_prediction_results.pages_list]
        document_prediction_results.paragraphs_len = [element[2] for element in
                                                      document_prediction_results.pages_list]
        document_prediction_results.paragraphs = [element[1] for element in document_prediction_results.pages_list]
        return document_prediction_results

    def create_prediction_string_for_paragraphs(self, paragraphs: list, detected_topics: list, xgboost_flag) -> List:
        predictions_strings = []
        for index, page_paragraphs in enumerate(paragraphs):
            if len(page_paragraphs) >= 1 and len(detected_topics[index].results) >= 1 and detected_topics[index].results[0] != ['none']:
                predictions_strings.append([index, self.service.prepare_results_to_output(
                    topic_results=[detected_topics[index]], paragraphs=page_paragraphs, acumulated_text=True,
                    xgboost_flag=xgboost_flag, string_representation=False)])
            else:
                result = TopicResult(results= [0.0, ['']])
                predictions_strings.append([index, result])
        return predictions_strings

    def extract_topics(self, predictions_strings: list) -> List:
        topic_document_filtered = []
        for predictions_string in predictions_strings:
            if len(predictions_string) >= 1:
                topic_document_filtered.append([predictions_string[0], predictions_string[1].results[0][0]])
            else:
                topic_document_filtered.append([])
        return topic_document_filtered

    def seperate_accumulated(self, document_prediction_results: DocumentObject, pages_id: List) -> [List, List]:
        topic_filtered = []
        topic_document_filtered_accumulated = []

        for index, pages in enumerate(document_prediction_results):
            len_topics = (len(pages[1]) - 1)
            if len(pages[1]) <= 1:
                topic_filtered.append(pages[1][len_topics:])
                topic_document_filtered_accumulated.append(pages[1][len_topics:])
            else:
                topic_filtered.append([pages_id[index], pages[1][:len_topics]])
                topic_document_filtered_accumulated.append(pages[1][len_topics:])

        return topic_filtered, topic_document_filtered_accumulated

    def make_proto_objects(self, detected_topics: list) -> List[TopicObjectProto]:
        proto_objects = []
        if len(detected_topics) > 1:
            for object in detected_topics:
                obj = TopicObjectProto(topic=str(object))
                proto_objects.append(obj)
        else:
            obj = TopicObjectProto(topic=str(detected_topics[0]))
            proto_objects.append(obj)
        return proto_objects

    def create_page_topics_proto(self, topic_document_extracted: [List], page_id_list: [List]) -> [PageTopicsProto]:
        page_protos = []
        for item in topic_document_extracted:
            try:
                page_topics = self.flatten_list(item[1])
                page_id = (page_id_list[item[0]])
                page = PageTopics(page_id=page_id, topics=page_topics)
                page_protos.append(page.proto())
            except Exception as e:
                logging.info("Error parsing page topics", e)
        return page_protos

    def nest_list(self, topic) -> list:
        print(topic)
        if len(topic)== 0:
            topic = [[[]]]
        if type(topic) != list:
            topic = [[[topic]]]
        elif type(topic[0]) != list:
            topic = [[topic]]
        else:
            if type(topic[0][0]) != list:
                topic = [topic]
        return topic

    def flatten_list(self, nested_list):
        # check if list is empty
        if not (bool(nested_list)):
            return nested_list

        # to check instance of list is empty or not
        if isinstance(nested_list[0], list):
            # call function with sublist as argument
            return self.flatten_list(*nested_list[:1]) + self.flatten_list(nested_list[1:])

        # call function with sublist as argument
        return nested_list[:1] + self.flatten_list(nested_list[1:])
