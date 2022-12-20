import logging
import pymongo
from bson import ObjectId
from datetime import datetime

from infrastructure.mongo_db import MongoDB
from models.document_object import DocumentObject
from models.mongo_model import MongoModel
from models.topic import Topic
from models.topic_collection import TopicCollection, TopicTrio, ParagraphTopicTrio
from models.topic_result import TopTopicResult


class DetectionResultRepository:

    def __init__(self, database: MongoDB, collection_name: str = None):
        if not collection_name:
            raise ValueError("No Collection name given!")
        self.collection_name = collection_name
        self.database = database
        self.create_index()

    def exists(self, document_id) -> bool:
        return self.database.get()[self.collection_name].count_documents(
            {'document_id': document_id}) > 0

    def exists_page(self, page_id) -> bool:
        return self.database.get()[self.collection_name].count_documents( {'pages.page_id': page_id}) > 0

    def store(self, detection_result: DocumentObject):
        if detection_result.id is None:
            detection_result.id = ObjectId()

        if detection_result.created_at is None:
            detection_result.created_at = datetime.now()
        detection_result.updated_at = datetime.now()

        if detection_result.project_id is None:
            detection_result.project_id = 'nan'

        if self.exists(detection_result.document_id) is True:
            self.__update(detection_result)
        else:
            self.__insert(detection_result)

    def __insert(self, detection_result: MongoModel) -> ObjectId:
        self.database.get()[self.collection_name].insert_one(detection_result.mongo())

    def __update(self, detection_result: MongoModel) -> ObjectId:
        return self.database.get()[self.collection_name].update_one({'_id': ObjectId(detection_result.id)},
                                                                    {'$set': detection_result.mongo()}, True)

    def delete_entries_by_document(self, document_id: str):
        try:
            bulk = self.database.get()[self.collection_name].initialize_unordered_bulk_op()
            bulk.find({
                'document_id': document_id,
            }).remove()
            return bulk.execute()
        except Exception as e:
            logging.error("Error deleting topics: " + str(e))
            raise e

    def delete_project(self, project_id: str):
        try:
            bulk = self.database.get()[self.collection_name].initialize_unordered_bulk_op()
            bulk.find({
                'project_id': project_id
            }).remove()
            bulk.execute()
            return bulk.execute()
        except Exception as e:
            logging.error("Error deleting topics: " + str(e))
            raise e

    def get_page_top_topics(self, page_id) -> [TopicTrio]:
        document = self.find_document_by_page_id(page_id)
        page_top_topics = []
        for page in document['pages']:
            if page['page_id'] == page_id:
                for top_topic in page['top_topics']:
                    if len(top_topic['results'][0][0]) == 3:
                        topic_trio = TopicTrio(
                            top_0=str(top_topic['results'][0][0][0]),
                            top_1=str(top_topic['results'][0][0][1]), top_2=str(top_topic['results'][0][0][2])).dict()
                        if topic_trio is not None:
                            page_top_topics.append(topic_trio)
        return page_top_topics

    def get_page_topics(self, page_id) -> [TopicCollection]:
        document = self.find_document_by_page_id(page_id)
        page_topics = []
        for page in document['pages']:
            if page['page_id'] == page_id:
                for topic in page['topics']:
                    topic_collection = []
                    for percent_word in topic['results'][1]:
                        percentage, word = percent_word.replace('"', '').replace(' ', '').split('*')
                        topic_collection.append(Topic(percentage=percentage, word=word))
                    page_topics.append(TopicCollection(percentage=topic['results'][0], topics=topic_collection))
        return page_topics

    def get_document_topics(self, document_id) -> list:
        document = self.find_document_by_ids(document_id)
        document_topics = []
        for topic in document['topics']:
            topic_collection = []
            for percent_word in topic['results'][1]:
                percentage, word = percent_word.replace('"', '').replace(' ', '').split('*')
                topic_collection.append(Topic(percentage=percentage, word=word))
            document_topics.append(TopicCollection(percentage=topic['results'][0], topics=topic_collection))
        return document_topics

    def get_document_top_topics(self, document_id) -> list:
        document = self.find_document_by_ids(document_id)
        trios = []
        for top_topics in document['top_topics']:
            for top_topic in top_topics['results']:
                if len(top_topic) == 3:
                    trios.append(TopicTrio(top_0= str(top_topic[0]),top_1 = str(top_topic[1]), top_2= str(top_topic[2])).dict())
        return trios

    # TODO: Refactor
    def get_page_paragraph_topics(self, page_id):
        if self.exists_page(page_id):
            document = self.find_document_by_page_id(page_id)
            page_paragraph_topics = []
            page_paragraph_positions = []
            for page in document['pages']:
                if page['page_id'] == page_id:
                    for paragraph in page['paragraphs']:
                        page_paragraph_positions.append(paragraph['position'])
                        for topics in paragraph['topics']:
                            if topics['results'][0] == 0.0:
                                paragraph_topics = ParagraphTopicTrio(percentage=topics['results'][0],
                                                                   topics=[Topic(percentage=0.0, word='')])
                                page_paragraph_topics.append(paragraph_topics)

                            elif len(topics['results']) == 2:
                                topic_collection = []
                                for percent_word in topics['results'][1]:
                                    percentage, word = percent_word.replace('"', '').replace(' ', '').split('*')
                                    topic_collection.append(Topic(percentage=percentage, word=word))
                                page_paragraph_topics.append(TopicCollection(percentage=topics['results'][0],
                                                                             topics=topic_collection))
                            else:
                                paragraph_topics = []
                                for topic in topics['results']:
                                    topic_collection = []
                                    for percent_word in topic['results'][1]:
                                        percentage, word = percent_word.replace('"', '').replace(' ', '').split('*')
                                        topic_collection.append(Topic(percentage=percentage, word=word))

                                    paragraph_topics.append(TopicCollection(percentage=topic['results'][0],
                                                                            topics=topic_collection))

                                    page_paragraph_topics.append(paragraph_topics)
            return page_paragraph_positions, page_paragraph_topics
        else:
            return [[0, 0]], TopicCollection(percentage=0.0, topics=[Topic(percentage=0.0, word='')])

    def get_page_paragraph_top_topics(self, page_id):
        document = self.find_document_by_page_id(page_id)
        page_paragraph_top_topics = []
        page_paragraph_positions = []
        for page in document['pages']:
            if page['page_id'] == page_id:
                for paragraph in page['paragraphs']:
                    page_paragraph_positions.append(paragraph['position'])
                    for top_topic in paragraph['top_topics']:
                        if len(top_topic['results']) == 0:
                            page_paragraph_top_topics.append(ParagraphTopicTrio(
                                    start_pos = int(paragraph['position'][0]), end_pos = int(paragraph['position'][1])))
                        else:
                            for topics in top_topic['results']:
                                for topic in topics:
                                    if len(topic) == 3:
                                        page_paragraph_top_topics.append(ParagraphTopicTrio(
                                            paragraph_top_0= str(topic[0]),paragraph_top_1 = str(topic[1]),
                                            paragraph_top_2= str(topic[2]),start_pos = int(paragraph['position'][0]), end_pos = int(paragraph['position'][1])).dict())
        return page_paragraph_top_topics

    def find_document_by_ids(self, document_id):
        to_find = {'document_id': document_id}
        if self.exists(document_id):
            return self.database.get()[self.collection_name].find_one(to_find)
        else:
            return None

    def find_document_by_page_id(self, page_id):
        to_find = {"pages.page_id": page_id}
        if self.exists_page(page_id):
            return self.database.get()[self.collection_name].find_one(to_find)
        else:
            return None

    def create_index(self):
        try:
            self.database.get()[self.collection_name].create_index(
                [('project_id', pymongo.ASCENDING),
                 ('document_id', pymongo.ASCENDING)])
            logging.info("Indexes created successfully")
        except Exception as e:
            logging.error("Failed creating indexes:", str(e))
