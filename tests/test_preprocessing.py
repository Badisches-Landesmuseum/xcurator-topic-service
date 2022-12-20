import unittest
from topic_modeling import parameter
from topic_modeling.preprocessing.text_clean_util import CleanUtil
from topic_modeling.preprocessing.text_preprocessing import TextPreprocessing


class TestPreprocessing(unittest.TestCase):

    def test_full_clean_text(self):
        test_text = '|;,.ä  ö'
        target_text = ' ae oe'
        clean_text = CleanUtil.full_clean_text(test_text, remove_special_chars=True, remove_short_sentences=True,
                                               expand_compound_words=True)
        self.assertEqual(clean_text, target_text, "Text is not cleaned correctly.")

    def test_full_clean_text(self):
        test_text = 'C:/Users/jfillies/Projects/topic-modeling/topic_modeling/resources/bpb_crawl_10000.html'
        parameter.initialize()
        nlp = TextPreprocessing.load_language_model('de_core_news_md')
        results = TextPreprocessing.open_html_clean(test_text, parameter.min_len_of_text, nlp)
        self.assertIsNotNone(results, "Html Text is not cleaned correctly.")


if __name__ == '__main__':
    unittest.main()
