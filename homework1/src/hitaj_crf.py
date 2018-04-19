__author__ = 'dorjan hitaj'
import pickle
from sklearn.linear_model import Perceptron
import sys, getopt
from itertools import chain
import pandas
import nltk
import sklearn
import scipy.stats
from sklearn.metrics import make_scorer
from sklearn.cross_validation import cross_val_score
from sklearn.grid_search import RandomizedSearchCV
import numpy as np
import sklearn_crfsuite
from sklearn_crfsuite import scorers
from sklearn_crfsuite import metrics


#converting all words in a file into labels
def allfilewords2label(file_name):

    file_handle = open(file_name)
    allwords2labels = dict()#the [word, corresponding_label] pairs will be stored in this dictionary

    for annotation_line in file_handle:
        # line_source_check = ':' in annotation_line
        if ':' in annotation_line: #the current line is of the trainning.eng.txt annotation style
            first_part = annotation_line.split(',') #consider only the first annotation
            first_part_splitted = first_part[0].split()
        else:  #the current line is of student annotation style
            first_part = annotation_line.split()
            first_part_splitted = first_part

        word_key = '*'+first_part_splitted[0]+'^'#the word plus (start end) tags that I will use as the key for its respective labbeling in the dictionary
        word_labelling = ''
        word_labelling += '*'
        for split_part in first_part_splitted[1:]:
                if ':' in annotation_line:
                    morpheme_lemma_pair = split_part.split(':')
                    morpheme = morpheme_lemma_pair[0]
                else:
                    morpheme = split_part
                morpheme_length = len(morpheme)
                if morpheme_length == 1: #if we are dealing with a single character morph
                    if morpheme != '~':
                        word_labelling += 'S'
                else:  #if we are dealing with multi-character morph
                        number_of_M = morpheme_length - 2 #2 places (begin and end are taken by B and E)
                        word_labelling += 'B'+'M'*number_of_M+'E'
        word_labelling += '^'
        if len(word_key) != len(word_labelling):
            word_labelling = word_labelling[0:len(word_labelling)-1]

        allwords2labels[word_key] = word_labelling
    return allwords2labels

#creating the feture set of a character in a word according to a given delta
def character2feature(word, character_index):
    index = character_index
    delta = 5 #after training and testing I let just the best performing delta based on the main training file, change as you plese for testing
    word_feature_dictionary = dict()#the character feature set will be stored in this dictionary
    # word_feature_dictionary['bias'] = 1
    for i in range(delta):
        #filling the right part feature set of the character
        if word[index:index+i+1] != "": #checking if going out of word bounds
            word_feature_dictionary['right_' + word[index:index+i+1]] = 1
        #filling the left one
        if word[index-i-1:index] != "":
            word_feature_dictionary['left_' + word[index-i-1:index]] = 1
    return word_feature_dictionary

#creating the full feture set for a word, thus all feature sets for every character in the word
def word2features(word):
    return [character2feature(word, i) for i in range(len(word))]

#calculating the precision, recall and f1 score by comparing the gold standard and the predicted output
def compute_precision_recall_fscore(gold_standard, predicted_output):
    precision = 0
    recall = 0
    fscore = 0
    results = dict()
    h = 0
    i = 0
    d = 0
    #iterate through all the labels and compute the h, i, d as advised in the homework description
    for j in range(len(gold_standard)):
        a = np.array(gold_standard[j])#convert the gold standard word label into a array of charactes
        b = np.array(predicted_output[j]) #also convert the corresponding predicted word label

        #get the array indixes where E and S are located in both gold standard and predicted labelling
        E_possitions_gold_standard=np.where(a == 'E')[0]
        E_possitions_predicted_output=np.where(b == 'E')[0]

        S_possitions_gold_standard=np.where(a == 'S')[0]
        S_possitions_predicted_output=np.where(b == 'S')[0]

        #calculating the correctly placed boundaries
        for ind in E_possitions_gold_standard:
            if(gold_standard[j][ind] == predicted_output[j][ind]):
                h = h+1

        for ind in S_possitions_gold_standard:
            if(gold_standard[j][ind] == predicted_output[j][ind]):
                h = h+1
        #calculating the incorrect boundaries
        for ind in E_possitions_predicted_output:
            if(predicted_output[j][ind] != gold_standard[j][ind]):
                i = i+1

        for ind in S_possitions_predicted_output:
            if(predicted_output[j][ind] != gold_standard[j][ind]):
                i = i+1
        #calculating the missing boundaries
        for ind in E_possitions_gold_standard:
            if(gold_standard[j][ind] != predicted_output[j][ind]):
                d = d+1

        for ind in S_possitions_gold_standard:
            if(gold_standard[j][ind] != predicted_output[j][ind]):
                d = d+1

    precision = float(h)/(h+i)
    recall = float(h)/(h+d)
    f1_score = float(2*precision*recall)/(precision+recall)

    results['precision'] = precision
    results['recall'] = recall
    results['f1_score'] = f1_score
    return results

#get user input for the files to be used for training, dev and test
training_file =raw_input('Type the training file name -->')
dev_file = raw_input('Type the dev file name -->')
test_file = raw_input('Type the test file name -->')

# train_file = 'files/combined.train.txt'
# train_file = 'files/training.eng.txt'
train_file = training_file
train_data = allfilewords2label(train_file)
all_training_words = train_data.keys()
X_train = [word2features(word) for word in all_training_words]
Y_train = list()

#populate the Y_train
for key, value in train_data.iteritems():
    Y_train.append(list(value))

dev_file = dev_file
dev_data = allfilewords2label(dev_file)
all_dev_words = dev_data.keys()
X_dev = [word2features(word) for word in all_dev_words]
Y_dev = list()
#populate the Y_dev
for key, value in dev_data.iteritems():
    Y_dev.append(list(value))

test_file = test_file
test_data = allfilewords2label(test_file)
all_test_words = test_data.keys()
X_test = [word2features(word) for word in all_test_words]
Y_test = list()
#populate the Y_test
for key, value in test_data.iteritems():
    Y_test.append(list(value))

crf = sklearn_crfsuite.CRF(
    algorithm='ap',
    max_iterations=100,
    all_possible_transitions=True,
    all_possible_states=True
)
crf.fit(X_train, Y_train, X_dev, Y_dev)
# pickle.dump(crf, open('extra_model.model', 'wb'))
# pickle.dump(crf, open('crf_model.model', 'wb'))

# labels = list(crf.classes_)
# print(labels)
y_pred = crf.predict(X_test)

# print metrics.flat_f1_score(Y_test, y_pred, average='weighted', labels=labels)
# sorted_labels = sorted(
#     labels,
#     key=lambda name: (name[1:], name[0])
# )
# print(metrics.flat_classification_report(
#     Y_test, y_pred, labels=sorted_labels, digits=3
# ))

# loaded_model = pickle.load(open('extra_model.model', 'rb'))
# loaded_model = pickle.load(open('crf_model.model', 'rb'))
# y_pred = loaded_model.predict(X_test)

test_results = compute_precision_recall_fscore(Y_test, y_pred)
print(test_results)


