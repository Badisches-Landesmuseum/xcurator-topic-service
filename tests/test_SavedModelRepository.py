'''import unittest
from tests import context
from topic_modeling.repositories.SavedModelRepository import SavedModelRepository

context.setup()


class TestSavedModelRepository(unittest.TestCase):

    def test_store(self):
        model = SavedModelRepository.get_LDAModel('lda_model')
        res = SavedModelRepository.store(model, 'test_model')
        self.assertTrue(res)


    def test_get_ldamodel(self):
        res= SavedModelRepository.get_LDAModel('lda_model')
        self.assertEqual(str(type(res)), "<class 'gensim.models.ldamodel.LdaModel'>", 'Not a gensim model returned')


    def test_get_hdpmodel(self):
        res = SavedModelRepository.get_HDPModel('HDP_model')
        self.assertEqual(str(type(res)), "<class 'gensim.models.hdpmodel.HdpModel'>", 'Not a gensim model returned')




if __name__ == '__main__':
    unittest.main()'''
