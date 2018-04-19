__author__ = 'dorjan'
import gensim
import numpy
from keras.utils import np_utils


# def make_word2vec_model():
#     print('...loading the word2vec model..')
#     models = dict()
#     models['model'] = gensim.models.KeyedVectors.load_word2vec_format('/home/dorjan/Downloads/GoogleNews-vectors-negative300.bin', binary=True)
#     # models['model_it'] = gensim.models.KeyedVectors.load_word2vec_format('/home/dorjan/Downloads/GoogleNews-vectors-negative300.bin', binary=True)
#     models['model_unknown'] = gensim.models.Word2Vec([['UNKNOWN']], min_count=1, size=300)
#     return models

def convert_file(file_path, window_size, modeL_english, model_italian, model_unknown):
    model = modeL_english
    model_unknown = model_unknown

    pos_tags = ['ADJ', 'ADV', 'INTJ', 'NOUN', 'PROPN', 'VERB', 'ADP', 'AUX', 'CONJ','DET', 'NUM', 'PART', 'PRON', 'SCONJ','PUNCT', 'SYM', 'X']
    label_to_indices = dict((c,i) for i, c in enumerate(pos_tags))
    indices_to_label = dict((i,c) for i,c in enumerate(pos_tags))

    x = []
    data_Y = []
    filehandle = open(file_path)

    sentences = []
    single_sentence = []

    sentence_count = 0
    for line in filehandle:
        if line.startswith('#'):
            sentence_count += 1
            single_sentence = []
            continue
        else:
            if len(line.rstrip()) == 0:
                #append to the big list
                sentences.append(single_sentence)
            else:
                splitted = line.split()
                word = splitted[1]
                tag = splitted[3]
                data_Y.append(label_to_indices[tag])
                single_sentence.append(word)

    y_train = np_utils.to_categorical(data_Y)
    padding_array = numpy.zeros(300)
    # window_size = window_size
    final_array = []
    word_context = []
    for seq in sentences:
        for i in range(len(seq)):
            word_context = []
            for j in range(window_size):
                #append to the left
                if (i-window_size+j) < 0:
                    word_context.append(padding_array)
                else:
                    if i-window_size+j>=0:
                        if seq[i-window_size+j] in model:
                            word_context.append(model[seq[i-window_size+j]])
                        else:
                            word_context.append(model_unknown['UNKNOWN'])
            if seq[i] in model:
                word_context.append(model[seq[i]])
            else:
                            word_context.append(model_unknown['UNKNOWN'])

            for j in range(window_size):
                #append to the left
                if (i+j) > len(seq)-1:
                    word_context.append(padding_array)
                else:
                    if i+j <= len(seq)-1:
                        if seq[i+j] in model:
                            word_context.append(model[seq[i+j]])
                        else:
                            word_context.append(model_unknown['UNKNOWN'])
            final_array.append(word_context)

    x = numpy.array(final_array)
    filehandle.close()
    data_dict = dict()

    data_dict['X_data'] = x
    data_dict['Y_data'] = y_train
    data_dict['window_size'] = window_size
    return data_dict


def convert_sentence(sentence, window_size, model_english, model_italian, model_unknown):
    model = model_english
    model_unknown = model_unknown

    x = []
    padding_array = numpy.zeros(300)
    final_array = []
    word_context = []

    for i in range(len(sentence)):
        word_context = []
        for j in range(window_size):
            #append to the left
            if (i-window_size+j) < 0:
                word_context.append(padding_array)
            else:
                if i-window_size+j>=0:
                    if sentence[i-window_size+j] in model:
                        word_context.append(model[sentence[i-window_size+j]])
                    else:
                        word_context.append(model_unknown['UNKNOWN'])
        if sentence[i] in model:
            word_context.append(model[sentence[i]])
        else:
                        word_context.append(model_unknown['UNKNOWN'])

        for j in range(window_size):
            #append to the right
            if (i+j) > len(sentence)-1:
                word_context.append(padding_array)
            else:
                if i+j <= len(sentence)-1:
                    if sentence[i+j] in model:
                        word_context.append(model[sentence[i+j]])
                    else:
                        word_context.append(model_unknown['UNKNOWN'])
        final_array.append(word_context)

    x = numpy.array(final_array)

    return x

def all_file_sentences(test_file_path):
    filehandle = open(test_file_path)
    sentences = list()
    for line in filehandle:
        if line.startswith('#'):
            single_sentence = []
            continue
        else:
            if len(line.rstrip()) == 0:
                #append to the big list
                sentences.append(single_sentence)
            else:
                splitted = line.split()
                word = splitted[1]
                single_sentence.append(word)

    filehandle.close()
    return sentences
