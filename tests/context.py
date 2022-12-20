import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import topic_modeling  # noqa # pylint: disable=unused-import, wrong-import-position

def setup():
    os.chdir('../')
    os.chdir(os.getcwd() + '/topic_modeling')

