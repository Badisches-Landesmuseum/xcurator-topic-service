import unittest
from topic_modeling.repositories.PickelRepository import PickelRepository
from topic_modeling.topic_matching_models.hdp import HDPModel
from topic_modeling.processing.text_processing import TextProcessing
from tests import context

context.setup()


class TestHDPModel(unittest.TestCase):
    def test_train(self):
        input_data = PickelRepository.get()
        input_data = input_data[:1000]
        data_dtm = TextProcessing.create_data_matrix(input_data)
        sw = TextProcessing.get_stopwords(input_data)
        class_dummy = HDPModel()
        res = HDPModel.train(class_dummy,[data_dtm, sw], 'HDPModel')
        failed_ouput = 'Problems with Training'
        self.assertNotEqual(failed_ouput, res, 'HDP train returns an empty or none instad of cluster array')


    def test_predict(self):
        input_data = PickelRepository.get()
        input_data = input_data[:1000]
        data_dtm = TextProcessing.create_data_matrix(input_data)
        sw = TextProcessing.get_stopwords(input_data)
        class_dummy = HDPModel()
        res = HDPModel.predict(class_dummy, [data_dtm, sw], 'HDPModel')
        failed_ouput = 'HDPModel not capable of making predictions.'
        self.assertNotEqual(failed_ouput, res, 'HDP predict returns an empty or none instad of cluster array')


if __name__ == '__main__':
    unittest.main()