__author__ = 'dorjan'

import sys
#sys.path.insert(0, '/home/dorjan/Desktop/homework_2')
import numpy
import gensim
from keras.models import Sequential
import homework2
import hitaj_utilities
import LSTMPOSTagger

class POSTaggerTester(homework2.AbstractPOSTaggerTester):
    def __init__(self, resource_dir):
        self._resource_dir = resource_dir
        self._model_english = None
        self._model_italian = None
        self._model_unknown = None
        print('POSTaggerTester class initialized successfully')

    def load_resources(self):
        print('...loading the word2vec models in POSTaggerTester..')
        # models = dict()
        # models['model_english'] = gensim.models.KeyedVectors.load_word2vec_format(self._resource_dir+'word-vectors-english', binary=True)
        # models['model_it'] = gensim.models.Word2Vec.load(self._resource_dir+'word-vectors-italian')
        # models['model_unknown'] = gensim.models.Word2Vec([['UNKNOWN']], min_count=1, size=300)
        self._model_english = gensim.models.KeyedVectors.load_word2vec_format(self._resource_dir+'word-vectors-english', binary=True)
        self._model_italian = gensim.models.Word2Vec.load(self._resource_dir+'word-vectors-italian')
        self._model_unknown = gensim.models.Word2Vec([['UNKNOWN']], min_count=1, size=300)
        # return models

    def test(self, postagger, test_file_path):
        print('POSTaggerTester is calling method test')
        data_train = hitaj_utilities.convert_file(test_file_path, 4, self._model_english, self._model_italian, self._model_unknown)
        x_test = data_train['X_data']
        y_test = data_train['Y_data']

        predictions = postagger.get_model().predict(x_test, 128)
        results = dict()
        correctly_predicted_pos = 0
        num_predicted = len(predictions)
        i = 0
        for prediction in predictions:
            predicted_tag_index = numpy.argmax(prediction)
            correct_tag_index = numpy.argmax(y_test[i])
            if predicted_tag_index == correct_tag_index:
                correctly_predicted_pos += 1
            i += 1

        precision = float(correctly_predicted_pos)/num_predicted
        recall = precision #no need to waste computational power since by definition given on homework2.py they are the same value
        coverage = len(predictions)/len(y_test)
        f1_score = float(2*precision*recall)/(precision+recall)

        results['precision'] = precision
        results['recall'] = recall
        results['coverage'] = coverage
        results['f1'] = f1_score

        results_file = open('results.txt', 'w')
        results_file.write('precision '+str(results['precision']))
        results_file.write("\n")
        results_file.write('recall '+str(results['recall']))
        results_file.write("\n")
        results_file.write('f1 '+str(results['f1']))
        results_file.write("\n")
        results_file.write('coverage '+str(results['coverage']))
        results_file.write("\n")
        results_file.close()

        #writing the sentences and their POS Tagged sequence in the file
        sentences = hitaj_utilities.all_file_sentences(test_file_path)
        pos_tagged_sentences = open('pos_tagged_sentences.txt', 'w')

        for sentence in sentences:
            predicted_tags = postagger.predict(sentence)
            pos_tagged_sentences.write(' '.join(sentence))
            pos_tagged_sentences.write('\n')
            pos_tagged_sentences.write(' '.join(predicted_tags))
            pos_tagged_sentences.write('\n')

        return results


