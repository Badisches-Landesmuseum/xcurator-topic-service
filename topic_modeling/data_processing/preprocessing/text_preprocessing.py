import json
import logging
import os
from data_processing.handlers.text_handler import TextHandler

class TextPreprocessing:

    def open_json_clean_bpb(self, path):
        print("Cleaning the data...")
        content_list = []
        themens = ['politik', 'internationales', 'geschichte', 'gesellschaft']
        article_themes = []
        article_path_json = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))) + path
        logging.info(path)

        with open(article_path_json) as json_file:
            objects = json.load(json_file)
        for single_object in objects.items():
            if single_object[1]['field_inhalt']:
                theme = single_object[1]['url'].split('/')[3]
                if theme in themens:
                    content = single_object[1]['field_inhalt']
                    content_list.append(content)
                    article_themes.append((theme))

        clean_texts = TextHandler.clean_text(self, content_list)

        return clean_texts, article_themes

    def open_json_clean(self, path):
        print("Cleaning the data...")
        content_list = []
        article_themes = []
        article_path_json = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))) + path
        with open(article_path_json, encoding = 'utf-8') as json_file:
            objects = json.load(json_file)
        for single_object in objects:
            if single_object['pages']:# and single_object['file']['url'] != '':
                pages = single_object['pages']
                #url = single_object['file']['url']
                #theme = url.split('/')[2].replace('www','').replace('.',' ')
                theme = single_object['file']['name']
                for page in pages:
                    content= page['html']
                    content_list.append(content)
                    article_themes.append((theme))
        clean_texts = TextHandler.clean_text(self, content_list)

        return clean_texts, article_themes
