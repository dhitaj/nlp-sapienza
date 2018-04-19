__author__ = 'dorjan'

import sys
import numpy
import gensim
import homework2
import hitaj_utilities
import keras
from keras.models import Sequential

class LSTMPOSTagger(homework2.AbstractLSTMPOSTagger):

    def __init__(self, model, resource_dir):
        self._model = model
        self._resource_dir = resource_dir
        self._model_english = None
        self._model_italian = None
        self._model_unknown = None
        print('LSTMPOSTagger class initialized successfully')

    def get_model(self):
        return self._model

    def load_resources(self):
        print('...loading the word2vec models in LSTMPOSTagger..')
        # models = dict()
        # models['model_english'] = gensim.models.KeyedVectors.load_word2vec_format(self._resource_dir+'word-vectors-english', binary=True)
        # models['model_it'] = gensim.models.Word2Vec.load(self._resource_dir+'word-vectors-italian')
        # models['model_unknown'] = gensim.models.Word2Vec([['UNKNOWN']], min_count=1, size=300)
        self._model_english = gensim.models.KeyedVectors.load_word2vec_format(self._resource_dir+'word-vectors-english', binary=True)
        self._model_italian = gensim.models.Word2Vec.load(self._resource_dir+'word-vectors-italian')
        self._model_unknown = gensim.models.Word2Vec([['UNKNOWN']], min_count=1, size=300)
        # return models

    def predict(self, sentence):
        """
        predict the pos tags for each token in the sentence.
        :param sentence: a list of tokens.
        :return: a list of pos tags (one for each input token).
        """
        converted_sentence_to_vector = hitaj_utilities.convert_sentence(sentence, 4, self._model_english, self._model_italian, self._model_unknown)

        #list of 17 universal part of speech tags that I need to check the indices after the prediction is done by the model
        pos_tags = ['ADJ', 'ADV', 'INTJ', 'NOUN', 'PROPN', 'VERB', 'ADP', 'AUX', 'CONJ','DET', 'NUM', 'PART', 'PRON', 'SCONJ','PUNCT', 'SYM', 'X']
        # label_to_indices = dict((c,i) for i, c in enumerate(pos_tags))
        indices_to_label = dict((i,c) for i,c in enumerate(pos_tags))

        #call to the Keras model predict method
        predictions = self._model.predict(converted_sentence_to_vector, 128)

        tags = []
        for prediction in predictions:
            #the tag with the highest probability is considered as the closest prediction to the real one, I use argmax to get that index
            predicted_tag_index = numpy.argmax(prediction)
            #I convert the index to the written representation of the POS tag by using the indices_to_label
            tags.append(indices_to_label[predicted_tag_index])

        return tags

