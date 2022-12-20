# topic-modeling

Jan Fillies | [3pc GmbH](https://www.3pc.de)    

Service for topic modeling. It is the process of learning, recognizing, and extracting these topics across a collection of documents.
this service enables different algorithms to test topic modeling based on the data provided by a crawler service also included in the project.
This is part of the Qurator project and aims to make huge archives easier to organize by organizing based on topics, also use cases in the story editor can be seen.

### Technology Stack
- [Python 3.6](https://www.python.org/)
- [Conda](https://www.anaconda.com/)
- [Spacy](https://spacy.io/)
- [pandas](https://pandas.pydata.org/)
- [scikit-learn](https://scikit-learn.org/)
- [tensorflow-gpu-1.15](https://www.tensorflow.org/install/gpu)
- [genism](https://github.com/RaRe-Technologies/gensim)
- [lda2vec-0.16.10](https://github.com/cemoody/lda2vec)

### External needed data

- Glove vocab. Download from: tbd. Put vocab.txt in topic-modeling\tm_service\resources
- Crawled data. Download from: tbd. Put vocab.txt in topic-modeling\tm_service\resources\crawled
- python -m spacy download de_core_news_md
- python -m spacy download en_core_web_md
 
 
### Short algorithm summary
#####Kmeans:
standard clustering algorithm, still number of clusters needed.
#####DBsearch:
Advanced clustering algorithm nur cluster number but distance and min count per cluster needed.
#####LSA 
Super fast but medium to poor results.
 
#####LDA:
Slower and good results
 
#####LDA2VecModel
Slow and better results. But no standard predict function.

#####HDP:

Good performance and average speed. Advantage is that the number of cluster is not needed. But finds more clusters in the data than  might needed or expected.
### Further insides
LDA2vec can't operate on a small data set and needs a lot of time on a medium sized one, LDA underperformed LDA2vec on medium inout size but is able to process a larger frame in reasonable time.
LDA2vec only works when the texts are longer, LDA performs okay on small texts too
 
For closer insight on algorithms see doc folder.
 
### PyCharm IDE and Conda Setup
To see fully gets the logs make sure to: 
##### Run > Edit Configuration >  Emulate terminal in output console
Install the environment with: 
```
conda env create -f environment.yml
```
Update the environment with: 
```
conda env update -f environment.yml
```
### Papers
- [Topic Modeling with LSA, PSLA, LDA & lda2Vec](https://medium.com/nanonets/topic-modeling-with-lsa-psla-lda-and-lda2vec-555ff65b0b05)

