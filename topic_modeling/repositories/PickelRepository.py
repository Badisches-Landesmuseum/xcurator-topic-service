import logging
import pickle
import warnings
from enum import Enum
from pathlib import Path

import sys

warnings.filterwarnings("ignore", category=UserWarning)

class PickelTypeChooser(Enum):
    Matrix = 1
    Topics = 2
    XGboost = 3
    CleanedData = 4

class PickelRepository():

    def __init__(self, model_path):
        self._paths = dict()
        #topic_modeling
        self._paths[PickelTypeChooser.Matrix] = Path(sys.path[0] + model_path + "/data_matrix/data_matrix.pickle")
        self._paths[PickelTypeChooser.Topics] = Path(sys.path[0] + model_path + '/raw_topics/topics.pickle')
        self._paths[PickelTypeChooser.XGboost] = Path(sys.path[0] + '/resources/models/'
                                                                    'trained_classification_models/400/nopro'
                                                                    '/xgbboost_grams')
        self._paths[PickelTypeChooser.CleanedData] = Path(sys.path[0] +model_path + "/cleaned_data/cleaned_data.plk")


    def get(self, type_pickel_save: PickelTypeChooser):
        path = self._paths[type_pickel_save]
        with open(path, "rb") as fp:
            loaded_data = pickle.load(fp)
        return loaded_data

    def cleaned_data_exists(self):
        path = self._paths[PickelTypeChooser.CleanedData]
        try:
            open(path, encoding='utf-8')
            return True
        except IOError:
            return False

    def _catch_exception_save(self, path, data):
        try:
            data.to_pickle(path)
            logging.info('Data saved.')
        except:
            raise ValueError(f"Not possible to save Pickeled instance")
            return False
        return True

    def store(self, data):
        path = self._paths[PickelTypeChooser.CleanedData]
        retrun_bool_save = self._catch_exception_save(path, data)
        return retrun_bool_save

    '''  def update_version(self, data):
        path = self._paths[PickelTypeChooser.XGboost]
        version = datetime.now().strftime('_%Y%m%d%H%M%S')
        path = os.path.join(path, version)
        retrun_bool_save = self._catch_exception_save(path, data)
        return retrun_bool_save'''