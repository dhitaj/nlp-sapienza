__author__ = 'dorjan hitaj'
import xml.etree.cElementTree as ET
import numpy
import os
import nltk
from collections import Counter
import signal
import spacy

nlp = spacy.load('en')

class TimeoutException(Exception):
    pass

def timeout_handler(signum, frame):
    raise TimeoutException

signal.signal(signal.SIGALRM, timeout_handler)

def countDotsUpTo(splitted_text, index1):
    whole = numpy.array(splitted_text[0:index1])
    s = numpy.where(whole == '.')[0]
    return len(s)

def checkDot(space_splitted, index1, index2_start):

    to_return = dict()
    dots = countDotsUpTo(space_splitted, index1)
    ind = numpy.array(space_splitted[index1-dots:index2_start-dots])

    s = numpy.where(ind == '.')[0]
    if len(s) > 0:
        to_return['answer'] = 0
        return to_return
    else:
        whole = numpy.array(space_splitted[0:index1-dots])
        s2 = numpy.where(whole == '.')[0]

        second_part = numpy.array(space_splitted[index2_start-dots:])
        s3 = numpy.where(second_part == '.')[0]
        if len(s2)>0 and len(s3)>0:
            sentence_start = int(s2[len(s2)-1])+1
            sentence_end = int(s3[0])+index2_start-dots

            sentence = ' '.join(space_splitted[sentence_start:sentence_end+1])
            # print('---> ', sentence)
        else:
            # sentence_end = index2_start-dots+1
            # sentence = ' '.join(space_splitted[0:sentence_end+1])
            # print('-> ', sentence)
            sentence = ' ==000== '
        x = ' '.join(ind)
        to_return['answer'] = 1
        to_return['between'] = x
        to_return['num_dots'] = dots

        to_return['sentence'] = sentence.strip()
        return to_return


def verbInPhrase(postagged_phrase):
   verbs_list = ['VB', 'VBD', 'VBG', 'VBN', 'VBP', 'VBZ']
   flag = 0
   print(postagged_phrase)
   for a in postagged_phrase:
    print(a[1])
    if a[1] in verbs_list:
        flag = 1
        break
    print(flag)
    return flag



# filehandle = '/home/dorjan/Desktop/merged_62'
verbs_list = ['VB', 'VBD', 'VBG', 'VBN', 'VBP', 'VBZ']
skip1 = '<corpus>'
skip2 = '</corpus>'
start = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
end = '</disambiguatedArticle>'
path = '/home/dorjan/Desktop/homework3_files'

articles_count = 0
lines_read = 0
files_count = 0
relational_instances = list()
relational_phrases = list()

for filename in os.listdir(path):

    lines_read = 0
    files_count += 1
    articles_list = list()
    article_string = ''
    fullname = os.path.join(path, filename)
    with open(fullname) as fileobject:
        for line in fileobject:
            if lines_read == 0:
                if not line.startswith(skip1):
                    if not line.startswith(start):
                        article_string += start+line
                        lines_read += 1
                    else:
                        article_string += line
                        lines_read += 1
                else:
                    lines_read = 0
            elif lines_read > 0:
                if line.startswith(start):
                    articles_list.append(article_string)
                    article_string = ''
                    article_string +=line
                    lines_read=1
                elif line.startswith(end):
                    article_string += line
                    articles_list.append(article_string)
                    article_string = ''
                    lines_read=0
                else:
                    if not line.startswith(skip2):
                        article_string += line

    print('Going to parsing: ', files_count)

    dori = 0
    article_c = 0
    error_count = 0

    for article in articles_list:
        article_c+=1
        signal.alarm(120)
        try:

            try:
                # print(article_c)
                tree = ET.ElementTree(ET.fromstring(article))
                root = tree.getroot()
                text = root.find('text')
                whole_text = text.text
                space_splitted = whole_text.split(' ')
                x = root.find('annotations')

                hyper_link_count = 0
                HL1_index_end=None
                HL1_index=None
                HL2_index_end=None
                HL2_index=None
                dot_counter = 0
                hyperlink_list = list()

                for atype in x.findall('annotation'):
                    annotation_index = atype.find('anchorStart')
                    annotation_index_end = atype.find('anchorEnd')
                    annotation_type = atype.find('type')
                    annotation_babelnet_id = atype.find('babelNetID')

                    if annotation_type.text == 'HL':
                        hl_dict = dict()
                        hl_dict['anchorStart'] = int(annotation_index.text)
                        hl_dict['anchorEnd'] = int(annotation_index_end.text)
                        hl_dict['babelnet_id'] = annotation_babelnet_id.text
                        hyperlink_list.append(hl_dict)

                for hyperlink1 in hyperlink_list:
                    for hyperlink2 in hyperlink_list:

                        if (hyperlink1['anchorStart'] < hyperlink2['anchorStart']) and (int(hyperlink2['anchorStart']) < int(hyperlink1['anchorStart'])+20):
                            try:
                                answer = checkDot(space_splitted, hyperlink1['anchorEnd'], hyperlink2['anchorStart'])
                                if answer['answer'] == 1:
                                    idict = dict()
                                    pos = answer['between'].split()
                                    k = nltk.pos_tag(pos)
                                    flag = 0
                                    for a in k:
                                        if a[1] in verbs_list:
                                            flag = 1
                                            break
                                    if flag == 1:
                                        idict['h1'] = ' '.join(space_splitted[hyperlink1['anchorStart']-answer['num_dots']:hyperlink1['anchorEnd']-answer['num_dots']])
                                        idict['h1_babelnet_id'] = hyperlink1['babelnet_id']
                                        idict['phrase'] = answer['between']
                                        idict['h2'] = ' '.join(space_splitted[hyperlink2['anchorStart']-answer['num_dots']:hyperlink2['anchorEnd']-answer['num_dots']])
                                        idict['h2_babelnet_id'] = hyperlink2['babelnet_id']
                                        idict['sentence'] = answer['sentence']
                                        relational_instances.append(idict)
                                        relational_phrases.append(answer['between'])
                                else:
                                    # print('breaking')
                                    break
                            except:
                                print('Error here')
            except:
                error_count+=1
        except TimeoutException:
            continue
        else:
            signal.alarm(0)
    print('Done processing: ', article_c-error_count, ' Numbe rof error articles ', error_count)

print('Going to relation cleaning...')
phrases_to_write = list()
instances_to_write = list()

counted_phrases = Counter(relational_phrases)

for key, value in counted_phrases.items():

    line = key.strip()
    phrase = unicode('x '+line+' y')
    parse_phrase = nlp(phrase)
    flag = 0
    for word in parse_phrase:
        dep = str(word.dep_)
        wtext = word.text
        wtext2 = str(wtext.encode('utf8'))
        if dep.find('subj')>-1 and wtext2.strip() == 'x':
            flag+=1
        if (dep.find('obj')>-1 or dep.find('comp')>-1 or dep.find('attr')>-1) and wtext2.strip() == 'y':
            flag+=1
    if value > 3 and flag == 2:
        phrases_to_write.append(key)


for relation_tuple in relational_instances:
    if relation_tuple['phrase'] in phrases_to_write:
        instances_to_write.append(relation_tuple)


print(len(phrases_to_write))
print(len(instances_to_write))
filehandle_p = open('phrases_100.txt', 'a')
for phrase in phrases_to_write:
    filehandle_p.write(phrase.encode('utf8'))
    filehandle_p.write('\n')


filehandle_i = open('instances_100.txt', 'a')
for phrase in instances_to_write:
    sent = phrase['sentence']
    # s = sent.encode('utf8')
    to_write = phrase['h1']+" | "+phrase['phrase']+" | "+phrase['h2']+" | "+sent+" | "+phrase['h1_babelnet_id']+" | "+phrase['h2_babelnet_id']
    filehandle_i.write(to_write.encode('utf8'))
    filehandle_i.write('\n')