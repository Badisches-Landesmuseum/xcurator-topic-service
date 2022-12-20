import unittest
from tests import context
from topic_modeling import parameter
from topic_modeling.repositories.PickelRepository import PickelRepository
import pandas as pd

context.setup()


class TestPickelRepository(unittest.TestCase):

    def test_get(self):
        pd = PickelRepository.get()
        self.assertEqual(str(type(pd)), "<class 'pandas.core.frame.DataFrame'>", 'Not a pandas dataframe returned')

    def test_exists(self):
        res = PickelRepository.exists()
        self.assertTrue(res)

    '''
    #this works but overrids he cleaned data, therefore excluded
    def test_store(self):
        parameter.initialize()
        parameter.path_to_save_pkl_cleaned_resources = "/resources/basic_cleaned_bpb_test.pkl"
        d = {'col1': [1, 2], 'col2': [3, 4]}
        df = pd.DataFrame(data=d)
        res = PickelRepository.store(df)
        parameter.path_to_save_pkl_cleaned_resources = "/resources/basic_cleaned_bpb.pkl"
        self.assertTrue(res)
    '''

if __name__ == '__main__':
    unittest.main()