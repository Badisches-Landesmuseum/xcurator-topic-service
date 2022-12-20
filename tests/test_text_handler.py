from unittest import TestCase

from topic_modeling.data_processing.handlers.text_handler import TextHandler


class TestTextHandler(TestCase):

    def __init__(self, *args, **kwargs):
        super(TestTextHandler, self).__init__(*args, **kwargs)
        self.text = "<p>Absatz 1</p><p>Absatz 2</p>"
        self.text_handler = TextHandler()

    def test_split_into_paragraphs(self):
        paragraphs = self.text_handler.split_into_paragraphs(self.text)
        self.assertEqual(len(paragraphs), 2)

    def test_remove_empty(self):
        paragraphs = ["Absatz 1", "Absatz 2", " "]
        result = self.text_handler.remove_empty(paragraphs)
        self.assertEqual(len(result), 2)
        self.assertEqual("Absatz 1", result[0])
        self.assertEqual("Absatz 2", result[1])
