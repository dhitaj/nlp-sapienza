__author__ = 'dorjan'

import numpy
from keras.utils import np_utils
import spacy
import nltk
from itertools import ifilter
import random
from constants import RELATION_POS_TAGS
from nltk import pos_tag


def convert_file(server_dump, model_english, model_unknown, maximum_sentence_length, label_to_indices):
    dataY = []
    filehandle = open(server_dump)

    sentences = []
    single_sentence = []
    sentence_count = 0
    l=0
    for line in filehandle:
        if l < 550000:
            sentence = line.split('\t')
            if len(sentence)==2:
                f = sentence[0].split()
                if len(f)>15:
                    continue
                sentences.append(sentence[0])
                tag = sentence[1]
                dataY.append(label_to_indices[tag.strip()])
            l += 1
    y = np_utils.to_categorical(dataY)
    padding_array = numpy.zeros(300)
    X_train_vec=[]
    Y_train_vec=[]

    i=0
    for line in sentences:
        sentence_vec=list()
        s = line.strip("?")
        data=s.split()
        for word in data:
            if word in model_english:
                vector=model_english[word]
            else:
                vector=model_unknown['UNK']
            sentence_vec.append(vector)
        if len(sentence_vec) > maximum_sentence_length:
            sentence_vec = []
            continue
        while len(sentence_vec) < maximum_sentence_length:
            sentence_vec.append(padding_array)
        X_train_vec.append(sentence_vec)
    X_train = numpy.array(X_train_vec)
    Y_train = y

    print(X_train.shape)
    print(Y_train.shape)
    data_dict = dict()

    data_dict['X_data'] = X_train
    data_dict['Y_data'] = Y_train
    return data_dict


def convert_sentence(sentence, model_english, model_unknown, maximum_sentence_length):
        X_vector = []
        sentence_vec = list()
        padding_array = numpy.zeros(300)
        s = sentence.strip("?")
        data = s.split()
        data1 = []
        if len(data) > maximum_sentence_length:
            data1 = data[0:maximum_sentence_length-1]
        else:
            data1=data
        for word in data1:
            if word in model_english:
                vector = model_english[word]
            else:
                vector = model_unknown['UNK']
            sentence_vec.append(vector)
        while len(sentence_vec) < maximum_sentence_length:
            sentence_vec.append(padding_array)
        X_vector.append(sentence_vec)
        X_test = numpy.array(X_vector)
        return X_test


def sentence_subjects(sentence):
    subjects = []
    nlp = spacy.load('en')
    parse_sentence = nlp(unicode(sentence))
    for word in parse_sentence:
        dep = str(word.dep_)
        wtext = word.text
        wtext2 = str(wtext.encode('utf8'))
        if dep.find('subj') > -1:
            subjects.append(wtext2)
    return subjects


def sentence_nouns(sentence):
    nouns = []
    verbs_list = ['NN', 'NNP', 'NNS']
    s = sentence.split()
    pos_tagged = nltk.pos_tag(s)
    for a in pos_tagged:
        if a[1] in verbs_list:
            nouns.append(a[0])
    return nouns


#filtering method suggested in online forums
def filter_by_relation(keyValList, exampleSet):
    filter_result = []
    for elem in ifilter(lambda x: x['relation'] in keyValList, exampleSet):
        filter_result.append(elem)
    return filter_result


def relation_to_ask(database_relations, domains_relations):
    not_used_relations = list()
    for lst in database_relations:
        if len(lst) > 0:
            for element in lst:
                if element['relation'].lower() in domains_relations:
                    continue
                else:
                    if element['relation'].lower() not in not_used_relations:
                        not_used_relations.append(element['relation'].lower())

    return not_used_relations[0]


def question_to_ask(relation, concept1, relation_patterns, domain_relations, domain):
    t = None
    if relation == 0:
        rel = domain_relations[domain.strip()]
        t = rel[random.randint(0, len(rel)-1)].lower()
        print(t)
        patterns = relation_patterns[t]
        r = random.randint(0, len(patterns)-1)
        question = patterns[r].replace('X', concept1)
    else:
        patterns = relation_patterns[relation]
        print relation
        t = relation
        r = random.randint(0, len(patterns)-1)
        question = patterns[r].replace('X', concept1)
    return question, t


def extract_answer_concept(concept1, relation, user_answer):
    concept2 = None
    rel = relation.upper()
    print(RELATION_POS_TAGS[rel])
    s = user_answer.split()
    concs = concept1.split()
    if len(s) == 1:
        return user_answer
    else:
        tokenized = pos_tag(s)
        print(tokenized)
        for tup in tokenized:
            print(tup[0])
            cnt = 0
            for wrd in concs:
                if tup[0].lower() == wrd[0].lower():
                    cnt += 1
            if cnt == 0 and tup[1] in RELATION_POS_TAGS[rel]:
                concept2 = tup[0]
                print(tup[1])
                break

    return concept2


def filter_yes_no(result_list):
    not_yes_no = ['Where', 'What', 'Who', 'Which', 'When', 'How', 'Why'
                  'where', 'what', 'who', 'which', 'when', 'how', 'why']
    filtered = list()
    for row in result_list:
        answer = row['question']
        splitted = answer.split()
        flag = False
        for s in splitted:
            if s.strip() in not_yes_no:
                flag = True
                break

        if flag is True:
            filtered.append(row)

    return filtered
