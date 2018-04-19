__author__ = 'dorjan'
from constants import RELATIONS
import gensim
import numpy
from keras.models import Model, load_model
from keras.layers import Dense, Dropout, Flatten, Input, MaxPooling1D, Convolution1D
from keras.layers.merge import Concatenate
import hitajutilities


class NeuralNetwork:

    def __init__(self, resource_dir):
        self._resource_dir = resource_dir
        self.maxlen = 15
        self._model_english = None
        self._model_unknown = None
        self.label_to_indices = dict((c, i) for i, c in enumerate(RELATIONS))
        self.indices_to_label = dict((i, c) for i, c in enumerate(RELATIONS))
        self.model = None

    def load_vectors(self):
        # self._model_english = gensim.models.KeyedVectors.load_word2vec_format(self._resource_dir+'w2v-word-vectors-english', binary=True)
        self._model_english = gensim.models.KeyedVectors.load_word2vec_format('data/w2v-word-vectors-english', binary=True)
        self._model_unknown = gensim.models.Word2Vec([['UNK']], min_count=1, size=300)

    def get_word2vec(self):
        return self._model_english

    def get_unknown_word2vec(self):
        return self._model_unknown

    def train(self, train_file):
        data_train = hitajutilities.convert_file(train_file,
                                                 self._model_english,
                                                 self._model_unknown,
                                                 self.maxlen,
                                                 self.label_to_indices)
        x_train = data_train['X_data']
        y_train = data_train['Y_data']

        filter_sizes = (3, 8)
        num_filters = 10
        dropout_prob = (0.5, 0.8)
        hidden_dims = 50
        batch_size = 64
        num_epochs = 10
        input_shape = (self.maxlen, 300)
        model_input = Input(shape=input_shape)
        z = model_input
        z = Dropout(dropout_prob[0])(z)
        conv_blocks = []
        for sz in filter_sizes:
            conv = Convolution1D(filters=num_filters,
                                 kernel_size=sz,
                                 padding="valid",
                                 activation="relu",
                                 strides=1)(z)
            conv = MaxPooling1D(pool_size=2)(conv)
            conv = Flatten()(conv)
            conv_blocks.append(conv)
        z = Concatenate()(conv_blocks) if len(conv_blocks) > 1 else conv_blocks[0]
        z = Dropout(dropout_prob[1])(z)
        z = Dense(hidden_dims, activation="relu")(z)
        model_output = Dense(16, activation="softmax")(z)

        model = Model(model_input, model_output)
        model.compile(loss="categorical_crossentropy", optimizer="adadelta", metrics=["accuracy"])
        model.fit(x_train, y_train, batch_size=batch_size, epochs=num_epochs,
                  validation_split=0.2, verbose=2)
        model.save('models/dori.model')
        return model

    def load_model(self, model_file):
        model = load_model('models/'+model_file)
        self.model = model
        return model

    def predict_relation(self, sentence):
        vector_list = list()
        vectorized_sentence = hitajutilities.convert_sentence(sentence, self._model_english, self._model_unknown, self.maxlen)
        vector_list.append(vectorized_sentence)
        # tensorflow complains about loaded models in class instances, that is why I have done the method below
        prediction = self.model.predict(vectorized_sentence, 64)
        predicted_tag_index = None
        for p in prediction:
            predicted_tag_index = numpy.argmax(p)
            print(p)
        relation = self.indices_to_label[predicted_tag_index]
        return relation

    def get_rel_w2v(self, question):
        label = ""
        X_train_vec = []
        padding = numpy.zeros(300)
        sentence_vec = list()
        s = question.strip("?")
        data = s.split()
        for word in data:
            if word in self._model_english:
                vector = self._model_english[word]
            else:
                vector = self._model_unknown['UNK']
            sentence_vec.append(vector)
        if len(sentence_vec) > self.maxlen:
            sentence_vec = sentence_vec[:15]
        while len(sentence_vec) < self.maxlen:
            sentence_vec.append(padding)
        X_train_vec.append(sentence_vec)
        X_train = numpy.array(X_train_vec)
        model = load_model('models/dori.model')
        y_predicted = model.predict(X_train, batch_size=32, verbose=2)
        for y in y_predicted:
            max_index = numpy.argmax(y)
            label = self.indices_to_label[max_index]

        return label
