import unittest
from topic_modeling.repositories.PickelRepository import PickelRepository
from topic_modeling.topic_matching_models.lda import LDAModel
from topic_modeling.processing.text_processing import TextProcessing
from tests import context

context.setup()


class TestLDAModel(unittest.TestCase):

    def test_train(self):
        input_data = PickelRepository.get()
        input_data = input_data[:1000]
        data_dtm = TextProcessing.create_data_matrix(input_data)
        sw = TextProcessing.get_stopwords(input_data)
        class_dummy = LDAModel()
        res = LDAModel.train(class_dummy, [data_dtm, sw], 'LDAModel')
        failed_ouput = 'Problems with Training'
        self.assertNotEqual(failed_ouput, res, 'LDAModel train returns an empty or none instad of cluster array')


def test_predict(self):
        expected_res = 'LDAModel not capable of making predictions.'
        input_data = PickelRepository.get()
        input_data = input_data[:1000]
        data_dtm = TextProcessing.create_data_matrix(input_data)
        sw = TextProcessing.get_stopwords(input_data)
        model = LDAModel()
        res = model.predict([data_dtm, sw], 'LDAModel')
        self.assertEqual(res, expected_res, "LDAModel predict not working.")


if __name__ == '__main__':
    unittest.main()