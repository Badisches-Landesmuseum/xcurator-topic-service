import logging
import os

import sys
from ai_model_repository import NexusRepository


class AIModelRepository:

    MODEL_DIR = os.path.join(sys.path[0], 'resources/models')

    def __init__(self, nexus_config: dict = None, modell_config: dict = None):
        if not nexus_config:
            raise ValueError("Please add a nexus config in our application.yml to enable the ai model repositoy")
        if not nexus_config['user']:
            raise ValueError("Nexus username is missing!")
        if not nexus_config['password']:
            raise ValueError("Nexus password is missing")
        if not modell_config['modell_name']:
            raise ValueError("No model is defined")

        self.nexus = NexusRepository(user = 'ai_user',password= 'ckcvdoHrP4o3Rczn')
        self.model_name = modell_config['modell_name']
        self.model_version = modell_config['version']

    def store_model(self,model_name, version: str = None):
        if not version:
            raise ValueError("No version is specified. Please add a version in the form: x.x.x")

        logging.info("start uploading the model!")
        model_path = os.path.join(self.MODEL_DIR, self.model_name)
        if not os.path.exists(model_path):
            raise ValueError(f"No model directory at path ({model_path}) exists.")
        self.nexus.upload("dreipc", model_name, version)
        self.model_version = version
        logging.info("finished uploading the model.")

    def get_model(self, force=False):
        if not os.path.exists(os.path.join(self.MODEL_DIR, self.model_name)) or force:
            self.nexus.download("dreipc", self.model_name, self.model_version)

    def get_specific_model(self, name: str, version: str, force=False):
        if not os.path.exists(os.path.join(self.MODEL_DIR, name)) or force:
            self.nexus.download("dreipc", name, version)
