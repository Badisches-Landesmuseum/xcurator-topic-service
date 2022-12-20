import logging

import spacy
from ariadne.asgi import GraphQL
from py_config.application_config import YamlConfig
from rabbitmq_proto_lib.manager import RabbitManager

from infrastructure.fastapi import FastAPIServer
from infrastructure.graphql import GraphQLConfiguration
from infrastructure.model_setup import ModelSetup
from infrastructure.mongo_db import MongoDB
from messaging.deletion_listener import DeletionRabbitListener
from messaging.detection_listener import TopicRabbitListener
from repositories.detection_result_repository import DetectionResultRepository
from resolvers.topic_modeling_resolver import TopicModelingResolver
from resources.resources_manager import ResourcesManager


class TopicModelingService:
    logging.basicConfig(level=logging.INFO)
    ResourcesManager.print_banner()
    logging.info('🚀 Topic Modeling Service is starting with spaCy v' + spacy.__version__)
    app_config = YamlConfig.load()
    model_setup = ModelSetup(app_config)
    topic_model = model_setup.creat_topic_model()

    mongodb = MongoDB(app_config['mongodb'])
    mongodb.connect()

    repository = DetectionResultRepository(mongodb, app_config['modell']['collection'])

    webserver = FastAPIServer(app_config['server'])

    # RabbitMQ Messaging
    rabbitmq = RabbitManager(app_config['rabbitmq'], app_name=app_config['service']['service_name'])
    detection_listener = TopicRabbitListener(topic_model, repository, app_config['modell']['project_id'])
    deletion_listener = DeletionRabbitListener(repository=repository, project_id=app_config['modell']['project_id'])

    rabbitmq.register(detection_listener)
    rabbitmq.register(deletion_listener)

    # GraphQL
    resolver = TopicModelingResolver(topic_model, repository)
    schema = GraphQLConfiguration(resolver).schema()
    webserver.register_endpoint("/graphql",
                                GraphQL(schema, debug=False,
                                        error_formatter=GraphQLConfiguration.dreipc_error_formatter))

    webserver.startup_event(rabbitmq.start)

    webserver.shutdown_event(rabbitmq.stop)
    webserver.shutdown_event(mongodb.disconnect())
    webserver.start()
