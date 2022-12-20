import logging

import xgboost as xgb
from sklearn import preprocessing
from sklearn.utils import shuffle

from repositories.PickelRepository import PickelRepository, PickelTypeChooser


class Xgboost():

    def __init__(self, model_path) -> None:
        self._xgboost = PickelRepository.get(PickelRepository(model_path), PickelTypeChooser.XGboost)

    def xgboost_predict(self, data):
        res = self._xgboost.predict(data)
        return res

    def train_xgboost(self, df, labels):
        df = preprocessing.normalize(df, norm='l2')
        df, labels = shuffle(df, labels, random_state=0)
        X = df
        y = labels
        n_split = int(len(df) * .9)
        X_train, X_test = X[:n_split], X[n_split:]
        y_train, y_test = y[:n_split], y[n_split:]

        # booster= 'dart'
        # , scale_pos_weight=5
        # ,num_parallel_tree=10
        xgb_model = xgb.XGBClassifier(objective="multi:softprob", tree_method='hist', num_parallel_tree=2,
                                      scale_pos_weight=100, n_estimators=1000, colsample_bytree=0.8,
                                      subsample=0.8, random_state=42, max_depth=10, learning_rate=0.02, gamma=0,
                                      eta=0.001, verbose=True, silent=0)

        xgb_model.fit(X_train, y_train)
        score = xgb_model.score(X_test, y_test)
        logging.info(score)
        PickelRepository.store(xgb_model)
        #pickle.dump(xgb_model, open('xgbboost_grams', 'wb'))


