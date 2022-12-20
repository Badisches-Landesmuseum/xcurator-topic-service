import unittest
from tests import context
from topic_modeling.repositories.JsonRepository import JsonRepository

context.setup()


class TestJsonRepository(unittest.TestCase):

    def test_get(self):
        json = JsonRepository.get()
        self.assertEqual(str(type(json[0])), "<class 'dict'>", 'Not a dict object returned')

    def test_exists(self):
        res = JsonRepository.exists()
        self.assertTrue(res)

    def test_store(self):
        res = JsonRepository.store('data')
        self.assertFalse(res)


if __name__ == '__main__':
    unittest.main()