import os


class ResourcesManager:

    def __init__(self, resources_config: dict = None):
        self.resources_config = resources_config

    @staticmethod
    def print_banner():
        print(open(os.path.join(os.path.dirname(__file__), "banner.txt")).read())
