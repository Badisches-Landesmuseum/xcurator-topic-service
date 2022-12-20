import unittest
from topic_modeling.repositories.PickelRepository import PickelRepository
from topic_modeling.topic_matching_models.lda2vec import LDA2VecModel
from tests import context

context.setup()


class TestLDA2VecModel(unittest.TestCase):

    def test_train(self):
        input_data = PickelRepository.get()
        input_data = input_data[:1000]
        class_dummy = LDA2VecModel()
        res = LDA2VecModel.train(class_dummy, input_data, 'lda2vec')
        failed_ouput = 'Problems with Training'
        self.assertNotEqual(failed_ouput, res, 'lda2vec train returns an empty or none instad of cluster array')

    def test_predict(self):
        expected_res = 'lda2vec not capable of making predictions.'
        input_data = PickelRepository.get()
        input_data = input_data[:1000]
        model = LDA2VecModel()
        res = model.predict(input_data, 'lda2vec')
        self.assertEqual(res, expected_res, "lda2vec predict not working.")


if __name__ == '__main__':
    unittest.main()