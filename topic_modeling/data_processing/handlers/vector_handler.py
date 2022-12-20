from sklearn.decomposition import PCA

from repositories.PickelRepository import PickelTypeChooser


class VectorHandler:

    def __init__(self, lda, pickelrepository, xgboost):
        self.pca = PCA(n_components=2)
        self._lda = lda
        self._topics = pickelrepository.get(PickelTypeChooser.Topics)
        self._Xgboost = xgboost

    def do_lda_xgboost_prediction(self, data_dtm_fitted):
        lda_results = VectorHandler.predict_topics(self, data_dtm_fitted)
        train_vec = lda_results[1]
        xgboost_results = VectorHandler.execute_xgboost_prediction(self, train_vec)
        return [lda_results[0], xgboost_results]

    def clean_lda_results(self, lda_results):
        lda_res = lda_results[0][0]
        lda_res.sort(key=lambda x: x[1], reverse=True)

        results = []
        for (a, b) in lda_res:
            for item in self._topics:
                if item[0] == a:
                    bags = item[1].split('+')
                    results.append([b, bags[:20]])
                    break
        return results

    def execute_xgboost_prediction(self, train_vec):
        xgboost_results = self._Xgboost.xgboost_predict(train_vec)
        return xgboost_results

    # ToDo Check if creating new PCA is painful (performance)
    def average_2d(self, vectors) -> (int, int):
        if vectors != [] and len(vectors) > 1:
            pca = self.pca.fit(vectors)
            vectors_2d = pca.transform(vectors)
            return (sum(vectors_2d[:, 0]) / len(vectors_2d[:, 0])), (sum(vectors_2d[:, 1]) / len(vectors_2d[:, 1]))
        else:
            return ((0.0) , (0.0))


    def flatten(self, paragraphs):
        flat_list = []
        for element in paragraphs:
            if isinstance(element, list):
                for item in element:
                    flat_list.append(item)
            else:
                flat_list.append(element)
        return flat_list

    def get_word_vectors(self, words: str):
        words = self._nlp(words)
        vectors = []
        for word in words:
            vectors.append(word.vector)
        return vectors
