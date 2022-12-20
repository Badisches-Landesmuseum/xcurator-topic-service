from typing import List

import pandas as pd
import sys
import os
from sklearn.feature_extraction.text import CountVectorizer
from text_preprocessing.text_clean_util import TextCleanUtil
import subprocess

import spacy


class TextHandler:

    def __init__(self, nlp_language):
        if nlp_language == 'DE':
            self._nlp = TextHandler.load_language_model('de_core_news_md')
            self.stop_words = self._get_stop_words()
        else:
            self._nlp = TextHandler.load_language_model('en_core_web_md')
            self.stop_words = self._get_stop_words_eng()

    def _get_stop_words(self):
        #topic_modeling/
        with open(sys.path[0] +"/resources/stop_words.txt", "r") as stop_word_file:
            return stop_word_file.read().split(',')

    def _get_stop_words_eng(self):
        # topic_modeling/
        with open(sys.path[0] + "/resources/stopwords_en.txt", "r") as stop_word_file:
            return stop_word_file.read().splitlines()

    @staticmethod
    def load_language_model(model_name: str):
        try:
            return spacy.load(model_name)
        except OSError:
            cmd_download = [sys.executable, "-m", "spacy", "download", model_name]
            cmd_link = [sys.executable, "-m", "spacy", "link", model_name, model_name]
            subprocess.call(cmd_download, env=os.environ.copy())
            subprocess.call(cmd_link, env=os.environ.copy())
            return spacy.load(model_name)

    # ToDo: Maybe some refactoring here related to performance!
    def split_into_paragraphs(self, text:str)-> (List, List):
        paragraphs_positions = []
        paragraph_break_p = '</p>'
        paragraph_break_br = '<br><br>'
        paragraph_break_b = '<br>'
        paragraphs = text

        if paragraph_break_p in text:
            paragraphs = text.split('</p>')

        if not isinstance(paragraphs, str):
            for index, element in enumerate(paragraphs):
                if paragraph_break_br in element:
                    paragraphs[index] = element.split('<br><br>')
                elif paragraph_break_b in element:
                    paragraphs[index] = element.split('<br>')
                else:
                    paragraphs[index] = element
            paragraphs = self._flattern(paragraphs)
        else:
            if paragraph_break_br in paragraphs:
                paragraphs = paragraphs.split('<br><br>')
            elif paragraph_break_b in paragraphs:
                paragraphs = paragraphs.split('<br>')
            else:
                paragraphs = paragraphs
        if isinstance(paragraphs, str):
            paragraphs = [paragraphs]

        old_paragraph_len = 0
        for index, paragraph in enumerate(paragraphs):
            paragraphs_positions.append([old_paragraph_len,old_paragraph_len+len(paragraph)])
            old_paragraph_len = old_paragraph_len + len(paragraph)
        return paragraphs, paragraphs_positions

    # ToDo: Maybe some refactoring here related to performance!
    def _flattern(self, paragraphs: List[str]) -> List[str]:
        flat_list = []
        for element in paragraphs:
            if isinstance(element, list):
                for item in element:
                    flat_list.append(item)
            else:
                flat_list.append(element)
        flat_list = [list for list in flat_list if list != []]
        return flat_list

    def remove_empty(self, paragraphs):
        special_html_tags = ["\n", "\n<p>", " ", "<p>",'</p>']
        paragraphs_clear = []
        deleted_indexes = []
        for index_paragraph_break_p, element_paragraph_break_p in enumerate(paragraphs):
            if element_paragraph_break_p not in special_html_tags and len(element_paragraph_break_p) > 3 and element_paragraph_break_p.isspace() != True:
                paragraphs_clear.append(element_paragraph_break_p)
                deleted_indexes.append(index_paragraph_break_p)

        return paragraphs_clear, deleted_indexes

    def clean_text(self, paragraphs: List[str]):
        texts = [TextCleanUtil.html_to_text(html) for html in paragraphs]
        texts = [TextCleanUtil.strip_accents_and_umlaute(text) for text in texts]
        texts = [TextCleanUtil.clean_with_alphabet(text, r'a-zA-ZöäüÖÄÜ0-9\s\.\,@\)\(\]\%\[\}\{\;\s:') for text in texts]
        texts = [TextCleanUtil.remove_words(text, self.stop_words) for text in texts]
        texts = [self.lemmatize_and_filter(text) for text in texts]
        return [self.check_for_str_length(text) for text in texts]


    def check_for_str_length(self, text:str)->str:
        if len(text.split(' '))>2:
            if len(text.split(' ')[0]) > 30 or len(text.split(' ')[1]) > 30:
                text = ''
        else:
            if len(text.split(' ')[0]) > 30:
                text = ''
        return text

    def lemmatize_and_filter(self, text: str):
        doc = self._nlp(text)
        # doc = ' '.join([word.lemma_ if word.lemma_ != '-PRON-' else word.text for word in doc])
        # only noun/pronpun and lemmatizer
        return ' '.join([word.lemma_ if (word.pos_ == 'NOUN' or word.pos_ == 'PROPN' or word.pos_ == 'VERB') else '' for word in doc])

    def to_vectors(self, text: str) -> List:
        return [word.vector for word in self._nlp(str(text))]

    def create_data_matrix(self, text):
        cv = self.get_count_vectorizer((text.iloc[0].tolist()))
        data_cv = cv.fit_transform(text.iloc[0])
        data_dtm = pd.DataFrame(data_cv.toarray(), columns=cv.get_feature_names())
        data_dtm.index = range(0, len(text.iloc[0]))
        return data_dtm, cv

    def get_count_vectorizer(self, text):
        #sw = self._get_stop_words()
        sw = self._get_stop_words_eng()
        cv = CountVectorizer(text, stop_words=sw, min_df=0.0002,
                             ngram_range=(1, 2))  # , min_df=0.0003, max_df=0.005)#, ngram_range=(1,1))#, min_df=1)
        return cv





