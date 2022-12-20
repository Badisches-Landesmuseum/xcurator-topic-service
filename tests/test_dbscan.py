import unittest
from topic_modeling.repositories.PickelRepository import PickelRepository
from topic_modeling.topic_matching_models.dbscan import DBScanModel
from topic_modeling.processing.text_processing import TextProcessing
from tests import context

context.setup()


class TestDBScanModel(unittest.TestCase):
    def test_train(self):
        expected_res = 'DBScan result: 18'
        input_data = PickelRepository.get()
        input_data = input_data[:1000]
        data_dtm = TextProcessing.create_data_matrix(input_data)
        class_dummy = DBScanModel()
        res = DBScanModel.train(class_dummy, data_dtm, 'DBScan')
        print(res)
        self.assertEqual(expected_res, res, 'DBscan training not working.')

    def test_predict(self):
        expected_res = 'DBscan not capable of making predictions.'
        input_data = PickelRepository.get()
        input_data = input_data[:1000]
        data_dtm = TextProcessing.create_data_matrix(input_data)
        model = DBScanModel()
        res = model.predict(data_dtm, 'DBscan')
        self.assertEqual(res, expected_res,"DBscan predict not working.")


if __name__ == '__main__':
    unittest.main()