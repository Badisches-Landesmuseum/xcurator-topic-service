import numpy as np
import pandas as pd
from pandas import DataFrame
from sklearn.feature_extraction.text import CountVectorizer

from repositories.PickelRepository import PickelRepository, PickelTypeChooser


class DataMatrix:

    def __init__(self, pickle_repository: PickelRepository):
        self.repository = pickle_repository
        self.training_matrix = pickle_repository.get(PickelTypeChooser.Matrix)
        self.training_matrix_empty = pd.DataFrame(np.zeros((1, len(self.training_matrix))))

    def create(self, text) -> DataFrame:
        if text != '' and text != ' ':
            count_vector = CountVectorizer(input=text, min_df=0.0002, ngram_range=(1, 2))
            pandas_data_frame = pd.DataFrame(columns=[0])
            pandas_data_frame.loc[0] = [text]
            data_count_vector = count_vector.fit_transform(pandas_data_frame[0])
            data_dtm = pd.DataFrame(data_count_vector.toarray(), columns=count_vector.get_feature_names())
            data_dtm.index = pandas_data_frame.index
        else:
            data_dtm = pd.DataFrame(columns=[0])
        return data_dtm

    def merge_to_superset_matrix(self, subset_matrix: DataFrame) -> DataFrame:
        superset_matrix = self.training_matrix_empty
        superset_matrix.columns = self.training_matrix
        subset_matrix = subset_matrix.filter(self.training_matrix)
        sub_super_matrix = pd.concat([superset_matrix, subset_matrix], axis=1)
        combined_sum = sub_super_matrix.groupby(sub_super_matrix.columns, axis=1).sum()
        return combined_sum
