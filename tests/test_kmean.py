import unittest
from topic_modeling.repositories.PickelRepository import PickelRepository
from topic_modeling.topic_matching_models.kmean import KMeanModel
from topic_modeling.processing.text_processing import TextProcessing
from tests import context

context.setup()

class TestKMeanModel(unittest.TestCase):
    def test_train(self):
        expected_res = 'Kmean result: Visualization KMean'
        input_data = PickelRepository.get()
        input_data = input_data[:1000]
        data_dtm = TextProcessing.create_data_matrix(input_data)
        class_dummy = KMeanModel()
        res = KMeanModel.train(class_dummy, data_dtm, 'Kmean')
        print(res)
        self.assertEqual(expected_res, res, 'Kmean training not working.')

    def test_predict(self):
        expected_res = 'Kmean not capable of making predictions.'
        input_data = PickelRepository.get()
        input_data = input_data[:1000]
        data_dtm = TextProcessing.create_data_matrix(input_data)
        model = KMeanModel()
        res = model.predict(data_dtm, 'Kmean')
        self.assertEqual(res, expected_res, "Kmean predict not working.")


if __name__ == '__main__':
    unittest.main()
