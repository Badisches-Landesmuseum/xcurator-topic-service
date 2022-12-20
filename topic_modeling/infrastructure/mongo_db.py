import logging

from pymongo import MongoClient


class MongoDB:

    def __init__(self, database_config):
        self.max_connection_count = 10
        self.min_connection_count = 10
        self.connection_string = f"mongodb://{database_config['username']}:{database_config['password']}" \
                                 f"@{database_config['host']}:{database_config['port']}/{database_config['database']}"
        self.database_name = database_config['database']
        self.client = None

    def connect(self):
        self.client = MongoClient(self.connection_string)
        print(self.connection_string)

    def disconnect(self):
        if self.client is None:
            logging.info("Database connection not initialized! Skip disconnect")
        else:
            self.client.close()

    def get(self) -> MongoClient:
        return self.client[self.database_name]
