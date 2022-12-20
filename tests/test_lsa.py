import unittest
from topic_modeling.repositories.PickelRepository import PickelRepository
from topic_modeling.processing.text_processing import TextProcessing
from topic_modeling.topic_matching_models.lsa import LSAModel
from tests import context

context.setup()


class TestLSAModel(unittest.TestCase):

    def test_train(self):
        input_data = PickelRepository.get()
        input_data = input_data[:1000]
        class_dummy = LSAModel()
        data_dtm = TextProcessing.create_data_matrix(input_data)
        res = LSAModel.train(class_dummy, data_dtm, 'lsaModel')
        failed_ouput = 'Problems with Training'
        self.assertNotEqual(failed_ouput, res, 'lsaModel train returns an empty or none instad of cluster array')

    def test_predict(self):
        expected_res = 'lsaModel not capable of making predictions.'
        input_data = PickelRepository.get()
        input_data = input_data[:1000]
        data_dtm = TextProcessing.create_data_matrix(input_data)
        model = LSAModel()
        res = model.predict(data_dtm, 'lsaModel')
        self.assertEqual(res, expected_res, "lsaModel predict not working.")


if __name__ == '__main__':
    unittest.main()