import logging

from scipy import spatial

from data_processing.handlers.vector_handler import VectorHandler


class OutputGeneration:

    def make_topic_output_string(self, lda_results, acumulated_text: bool):
        output_string = []
        for lda_result in lda_results:
            position_of_accumulated_text = len(lda_result) - 1
            for index, element in enumerate(lda_result):
                for sub_index, sub_element in enumerate(element):
                    if index == position_of_accumulated_text and acumulated_text:
                        output_string.append('Accumulated Text: ' + str(sub_element[1]))
                    else:
                        output_string.append('Paragraph: ' + str(index) + ' ' + str(sub_element[1]))
        return output_string

    def make_topic_output_list(self, lda_results, acumulated_text: bool):
        output_string = []
        for lda_result in lda_results:
            position_of_accumulated_text = len(lda_result) - 1

            for index, element in enumerate(lda_result):
                output_string_paragraph = []
                for sub_index, sub_element in enumerate(element):
                    if index == position_of_accumulated_text and acumulated_text:
                        output_string_paragraph.append([sub_element[1]])
                    else:
                        output_string_paragraph.append(sub_element[1])
                output_string.append(output_string_paragraph)
        return output_string

    def make_classification_output_string(self, predictions):
        label_names = ["Internationales", "Politik", "Geschichte", "Gesellschaft"]
        return label_names[int(predictions[1][0])]

    # get words that are closest to the middle point of the input paragraph
    def find_words_inpotic_closest_to_input(self, predictions, middle_point, vector_handler: VectorHandler):
        result_word_collection = []
        if len(predictions)>0:
            for list_index, prediction_item in enumerate(predictions):
                list_of_clusters = []
                best_fitting_words = []
                pure_word_list = OutputGeneration.make_list_of_words(self, prediction_item[1])
                vectors_2d = OutputGeneration.get_vectors_of_list_pca_transformed(self, pure_word_list, vector_handler)
                best_word, vectors_2d = OutputGeneration. \
                    find_closest_n_and_remove_from_vectors(self, vectors_2d, middle_point, 1)
                closest_three_best_word, vectors_2d = OutputGeneration. \
                    find_closest_n_and_remove_from_vectors(self, vectors_2d, best_word, 3)
                list_of_clusters.append([best_word, closest_three_best_word[1], closest_three_best_word[2]])
                best_fitting_words = OutputGeneration. \
                    insert_not_existing_bestfits(self, vectors_2d, best_fitting_words, pure_word_list, list_of_clusters)
                result_word_collection.append([list_index, best_fitting_words[:3]])
        return result_word_collection

    def find_closest_n_and_remove_from_vectors(self, vectors_2d, middle_point, number_of_close_points):
        best_word = OutputGeneration.get_closest_points(
            self, middle_point, vectors_2d, number_of_close_points)
        if len(best_word) == 2:
            vectors_2d = OutputGeneration.filter_out_best_word(self, vectors_2d, best_word)
        else:
            vectors_2d = OutputGeneration.filter_out_closest(self, vectors_2d, best_word)
        return best_word, vectors_2d

    def get_closest_points(self, point_of_interesst, vectors_2d, number_of_close_points):
        closest = vectors_2d[spatial.KDTree(vectors_2d).query(point_of_interesst, k=number_of_close_points)[1]]
        return closest

    def get_vectors_of_list_pca_transformed(self, pure_word_list, vector_handler: VectorHandler):
        vectors_topics = OutputGeneration.get_vector_topic_for_list(self, pure_word_list)
        vectors_2d = vector_handler.pca.transform(vectors_topics)
        return vectors_2d

    def make_list_of_words(self, word_string):
        pure_word_list = []
        for idx, word in enumerate(word_string):
            word_percent = word.split('*')
            word_pure = word_percent[1].replace('"', '').replace(' ', '')
            pure_word_list.append(word_pure)
        return pure_word_list

    def get_vector_topic_for_list(self, pure_word_list):
        vectors_topics = []
        for word in pure_word_list:
            vectors_topics.append(VectorHandler.get_word_vectors(self, word)[0])
        return vectors_topics

    def filter_out_best_word(self, vectors_2d, best_word):
        for i, a in enumerate(vectors_2d):
            comp = a == best_word
            if comp.all():
                # TODO find better way for this
                vectors_2d[i] = [vectors_2d[i][0] + 1000, vectors_2d[i][1] + 1000]
        return vectors_2d

    def filter_out_closest(self, vectors_2d, closest_word):
        for i, a in enumerate(vectors_2d):
            for x in closest_word:
                comp = a == x
                if comp.all():
                    # TODO find better way for this
                    map(lambda x: x + 1000, vectors_2d[i])
        return vectors_2d

    def insert_not_existing_bestfits(self, vectors_2d, best_fits, pure_word_list, list_of_clusters):
        for index_vector_list, value_vector_list in enumerate(vectors_2d):
            for word in list_of_clusters:
                for z in word:
                    comp = value_vector_list == z
                    if comp.all():
                        best_fits.insert(len(best_fits), pure_word_list[index_vector_list]) if pure_word_list[
                                                                                                   index_vector_list] not in best_fits else best_fits
        return best_fits

    def make_result_set(self, paragraph_topics_cleaned, xgboost_results, deleted_indexes, xgboost_flag):
        result_set = []
        for index, topic in enumerate(paragraph_topics_cleaned):
            if xgboost_flag:
                if index + 1 not in deleted_indexes:
                    result_set.append([topic, [xgboost_results[index].item(0)]])
                else:
                    result_set.append([])
                    result_set.append([topic, [xgboost_results[index].item(0)]])
            else:
                if index + 1 not in deleted_indexes:
                    result_set.append([topic])
                else:
                    result_set.append([])
                    result_set.append([topic])
        return result_set

    def text_empty_test(self, text):
        if text is None or len(text) == 0:
            logging.info("Logged Error: Not enough text given!")
