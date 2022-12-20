import logging
import os
from enum import Enum
from pathlib import Path

import sys
from gensim import models


class GensimModelChooser(Enum):
    LDA = 1
    HDP = 2


class GensimModelRepository():

    def __init__(self, model_path, model_nexus_name):
        self._base_path = Path(sys.path[0] + model_path)
        self._models = dict()
        self._models[GensimModelChooser.LDA] = str(model_nexus_name)
        self._models[GensimModelChooser.HDP] = 'hdp_model_mal'

    def _model_loader(self, gensim_model: GensimModelChooser):
        switcher = {
            GensimModelChooser.LDA: models.LdaModel,
            GensimModelChooser.HDP: models.HdpModel
        }
        return switcher.get(gensim_model, lambda: 'Unknown gensim_model_instance')

    def _model_saver(self, model, file):
        try:
            print(file)
            model.save(file)
        except Exception():
            raise ValueError(f"Not possible to save gensim_model_instance")
        return True

    def get(self, gensim_model: GensimModelChooser):
        path = os.path.join(self._base_path, self._models[gensim_model])
        lda = self._model_loader(gensim_model).load(str(path))
        return lda

    def store(self, gensim_model_instance, gensim_model: GensimModelChooser):
        # self._models[gensim_model]
        path = os.path.join(self._base_path, 'lda_model_mal_long')
        print(path)
        return self._model_saver(gensim_model_instance, str(path))
    '''
    def update_version(self, gensim_model_instance, gensim_model: GensimModelChooser, version: str):
        path = os.path.join(self._base_path, self._models[gensim_model], version)
        temp_file = datapath(path)
        return self._model_saver(self, gensim_model_instance, temp_file)'''
