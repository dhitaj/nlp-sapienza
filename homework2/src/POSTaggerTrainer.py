__author__ = 'dorjan'

import sys
import numpy
import gensim
from keras.models import Sequential
from keras.layers import Dense
from keras.layers import LSTM
from keras.layers import Dropout
from keras import constraints
from keras.optimizers import SGD
from keras import callbacks

import hitaj_utilities

import homework2


class POSTaggerTrainer(homework2.AbstractPOSTaggerTrainer):
    def __init__(self, resource_dir):
        self._resource_dir = resource_dir
        self._model_english = None
        self._model_italian = None
        self._model_unknown = None
        print('POSTaggerTrainer class initialized successfully')


    def load_resources(self):
        print('...loading the word2vec models in POSTaggerTrainer..')
        # models = dict()
        # models['model_english'] = gensim.models.KeyedVectors.load_word2vec_format(self._resource_dir+'word-vectors-english', binary=True)
        # models['model_it'] = gensim.models.Word2Vec.load(self._resource_dir+'word-vectors-italian')
        # models['model_unknown'] = gensim.models.Word2Vec([['UNKNOWN']], min_count=1, size=300)
        self._model_english = gensim.models.KeyedVectors.load_word2vec_format(self._resource_dir+'word-vectors-english', binary=True)
        self._model_italian = gensim.models.Word2Vec.load(self._resource_dir+'word-vectors-italian')
        self._model_unknown = gensim.models.Word2Vec([['UNKNOWN']], min_count=1, size=300)
        # return models

    def train(self, training_path):
        print('Entered in train method of POSTagger class')
        data_train = hitaj_utilities.convert_file(training_path, 4, self._model_english, self._model_italian, self._model_unknown)
        x_train = data_train['X_data']
        y_train = data_train['Y_data']

        x_dev = 0
        y_dev = 0
        window_size = data_train['window_size']
        print(x_train.shape)
        print(y_train.shape)
        print('Build model...')
        model = Sequential()
        model.add(LSTM(160, activation='tanh', kernel_initializer='uniform', recurrent_activation='sigmoid',
                        recurrent_dropout=0.1, input_shape=(window_size*2+1,300), return_sequences=True,
                    recurrent_constraint=constraints.maxnorm(3)))
        model.add(LSTM(75, activation='tanh', kernel_initializer='uniform',))
        model.add(Dropout(0.1))
        model.add(Dense(17, activation='softmax'))

        sgd = SGD(lr=0.1, decay=1e-5, momentum=0.9, nesterov=True)
        reduce_lr = callbacks.ReduceLROnPlateau(monitor='val_loss', factor=0.5, patience=0, min_lr=0.001, verbose=1)

        model.compile(loss='categorical_crossentropy', optimizer=sgd, metrics=['accuracy'])
        print('Train...')
        model.fit(x_train, y_train, batch_size=180,  callbacks=[reduce_lr], epochs=1)

        return model
