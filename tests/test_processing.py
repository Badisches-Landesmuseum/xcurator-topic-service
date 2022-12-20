import unittest

from topic_modeling.preprocessing.text_clean_util import CleanUtil


class TestPreprocessing(unittest.TestCase):

    def test_get_stop_words_nlk(self):
        clean_text = CleanUtil.get_stop_words_nlkt()
        self.assertIsNotNone(clean_text,'No stop words recived')


if __name__ == '__main__':
    unittest.main()
