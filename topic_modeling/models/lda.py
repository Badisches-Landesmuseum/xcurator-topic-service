import logging
import os

import pandas as pd
import scipy.sparse
import sys
from gensim import matutils, models

from repositories.GensimModelRepository import GensimModelRepository, GensimModelChooser

logging.getLogger("gensim").setLevel(logging.WARNING)


class LDAModel():

    def __init__(self, model_path, model_nexus_name) -> None:
        self._lda = GensimModelRepository.get(GensimModelRepository(model_path, model_nexus_name), GensimModelChooser.LDA)
        print(self._lda)

    def train_lda(self, input_list: list, model, number_of_topics: int):
        encodeddata = input_list[0]
        dictionarywithlocation = input_list[1]
        labels = input_list[2]
        tdm = encodeddata.transpose()
        sparse_counts = scipy.sparse.csr_matrix(tdm)
        corpus = matutils.Sparse2Corpus(sparse_counts)
        id2word = dict((v, k) for k, v in dictionarywithlocation.vocabulary_.items())

        os.environ['MALLET_HOME'] = sys.path[0] + '/resources/mallet-2.0.8'
        mallet_path = sys.path[0] + '/resources/mallet-2.0.8/bin/mallet'

        lda_mal = models.wrappers.LdaMallet(mallet_path, corpus=corpus, id2word=id2word,
                                            num_topics=number_of_topics)



        #lda_mal = models.LdaModel.load("lda_wraped.gensim")
        #self._lda = lda_mal



        lda_mal = models.wrappers.ldamallet.malletmodel2ldamodel(lda_mal)
        lda_mal.save("siemensv3_lda_wraped.gensim")
        self.lda_mal = lda_mal
        self._lda = self.lda_mal




        #temp_file = datapath("lda_mal.gensim")
        #lda_mal.save(temp_file)



        #temp_file = datapath("lda_wraped.gensim")


        #temp_file = datapath("lda_mal.gensim")
        #lda_mal.save(temp_file)

        #gmr = GensimModelRepository('/resources/models/bpb-topic-modeling-long/')
        #print('store')
        #print(gmr)
        #GensimModelRepository.store(gmr, lda_mal, model)

        print(corpus)
        print(input_list[0])
        train_vecs = self.converting_topics_to_featurevectors(self, input_list=input_list[0], corpus=corpus)

        if len(labels) > 0:
            s = pd.Series(labels)
        else:
            s = []
        labels, levels = pd.factorize(s)

        return [train_vecs, labels, levels], lda_mal.print_topics(num_topics=-1)


    def get_topics_for_list(self, input_list: list, model, number_of_topics: int):
        encodeddata = input_list[0]
        #dictionarywithlocation = input_list[1]
        labels = input_list[2]
        tdm = encodeddata.transpose()
        sparse_counts = scipy.sparse.csr_matrix(tdm)
        corpus = matutils.Sparse2Corpus(sparse_counts)
        #id2word = dict((v, k) for k, v in dictionarywithlocation.vocabulary_.items())


        #lda_mal = LDAModel('/resources/models/bpb-topic-modeling')

        self._lda = self.lda_mal


        topics = self.lda_mal.get_document_topics(corpus=corpus)

        print(topics)
        #print('hi')
        #lda_mal = models.wrappers.ldamallet.malletmodel2ldamodel(lda_mal)
        #lda_mal.save("lda_wraped.gensim")

        #temp_file = datapath("lda_mal.gensim")
        #lda_mal.save(temp_file)



        #temp_file = datapath("lda_wraped.gensim")


        #temp_file = datapath("lda_mal.gensim")
        #lda_mal.save(temp_file)

        #gmr = GensimModelRepository('/resources/models/bpb-topic-modeling-long/')
        #print('store')
        #print(gmr)
        #GensimModelRepository.store(gmr, lda_mal, model)

        print(corpus)
        print(input_list[0])
        train_vecs = self.converting_topics_to_featurevectors(input_list=input_list[0], corpus=corpus)

        if len(labels) > 0:
            s = pd.Series(labels)
        else:
            s = []
        labels, levels = pd.factorize(s)

        return [train_vecs, labels, levels], self.lda_mal.print_topics(num_topics=-1)


    def converting_topics_to_featurevectors(self, input_list, corpus):
        train_vecs = []
        for i in range(len(input_list)):
            top_topics = self._lda.get_document_topics(corpus[i], minimum_probability=0.0, )
            try:
                topic_vec = [top_topics[j][1] for j in range(self._lda.num_topics)]
            except ValueError:
                raise ValueError("Error: chosen number of topics is to big or to small for the input data!")
            train_vecs.append(topic_vec)
        return train_vecs

    def predict(self, input_list):
        encodeddata = input_list
        tdm = encodeddata.transpose()
        sparse_counts = scipy.sparse.csr_matrix(tdm)
        corpus = matutils.Sparse2Corpus(sparse_counts)
        train_vecs = LDAModel.converting_topics_to_featurevectors(self, input_list, corpus)
        lda_predic = self._lda[corpus]
        topic_list = []
        for topic in lda_predic:
            topic_list.append(topic)
        return [[topic_list], train_vecs]
