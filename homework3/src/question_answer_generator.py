__author__ = 'dorjan hitaj'
import random

def generate_positive_answer_pairs(patterns, triples, relation):
    filehandle = open('question-answer-pairs2.txt', 'a')
    count = 0
    for t in triples:
        line = t.split('|')
        concept1 = line[0].strip()
        concept2 = line[2].strip()
        sentence = line[3].strip()
        if line[5].strip() != '-1':
            disambiguated1 = concept1+"::"+line[5].strip()
        else:
            disambiguated1 = concept1+"::"
        if line[7].strip() != '-1':
            disambiguated2 = concept2+"::"+line[7].strip()
        else:
            disambiguated2 = concept2+"::"

        for pattern in patterns:
            if 'Y' in pattern:
                question = pattern.replace('X', concept1)
                question = question.replace('Y', concept2)
                answer = 'Yes'
                filehandle.write("{}\t{}\t{}\t{}\t{}\t{}".format(question, answer.strip(), relation,  sentence, disambiguated1, disambiguated2))
                filehandle.write("\n")
                count += 1
            else:
                question = pattern.replace('X', concept1)
                answer = concept2
                filehandle.write("{}\t{}\t{}\t{}\t{}\t{}".format(question.strip(), answer.strip(), relation.strip(), sentence.strip(), disambiguated1.strip(), disambiguated2.strip()))
                filehandle.write("\n")
                count += 1

    print(relation, " positive ", count)

def generate_negative_answer_pairs(patterns, triples, relation):
    filehandle = open('question-answer-pairs2.txt', 'a')
    count = 0
    for t in triples:
        line = t.split('|')
        concept1 = line[0].strip()
        concept2 = line[2].strip()
        sentence = line[3].strip()
        for pattern in patterns:
            if 'Y' in pattern:
                question = pattern.replace('X', concept1)
                random_line = triples[random.randint(0, len(triples)-1)]
                r_l = random_line.split('|')
                negative_concept1 = r_l[0].strip()
                negative_concept2 = r_l[2].strip()
                if (concept2 != negative_concept2) and (concept1 != negative_concept1):
                    question = question.replace('Y', negative_concept2)
                    answer = 'No'
                    filehandle.write("{}\t{}\t{}\t{}\t{}\t{}".format(question.strip(), answer.strip(), relation.strip(),  sentence.strip(), concept1.strip(), negative_concept2.strip()))
                    filehandle.write("\n")
                    count += 1
    print(relation, " negative ", count)

filehandle_patterns = open('patterns.tsv')

my_relations = ['activity', 'shape', 'similarity', 'colorPattern', 'howToUse']

patterns_activity = list()
patterns_shape = list()
patterns_similarity = list()
patterns_colorPattern = list()
patterns_howToUse = list()

patterns_dict = dict()

for line in filehandle_patterns:
    pattern_line = line.split('\t')
    if pattern_line[1].strip() == 'activity':
        patterns_activity.append(pattern_line[0].strip())
    elif pattern_line[1].strip() == 'shape':
        patterns_shape.append(pattern_line[0].strip())
    elif pattern_line[1].strip() == 'similarity':
        patterns_similarity.append(pattern_line[0])
    elif pattern_line[1].strip() == 'colorPattern':
        patterns_colorPattern.append(pattern_line[0].strip())
    else:
        patterns_howToUse.append(pattern_line[0].strip())

patterns_dict['activity'] = patterns_activity
patterns_dict['shape'] = patterns_shape
patterns_dict['similarity'] = patterns_similarity
patterns_dict['colorPattern'] = patterns_colorPattern
patterns_dict['howToUse'] = patterns_howToUse



filehandle_triples = open('triples/disambiguated_triples_sentence.tsv')

triples_activity = list()
triples_shape = list()
triples_similarity = list()
triples_colorPattern = list()
triples_howToUse = list()

triples_dict = dict()

for line in filehandle_triples:
    triple_line = line.split('|')
    if triple_line[1].strip() == 'activity':
        triples_activity.append(line)
    elif triple_line[1].strip() == 'shape':
        triples_shape.append(line)
    elif triple_line[1].strip() == 'similarity':
        triples_similarity.append(line)
    elif triple_line[1].strip() == 'colorPattern':
        triples_colorPattern.append(line)
    else:
        triples_howToUse.append(line)

triples_dict['activity'] = triples_activity
triples_dict['shape'] = triples_shape
triples_dict['similarity'] = triples_similarity
triples_dict['colorPattern'] = triples_colorPattern
triples_dict['howToUse'] = triples_howToUse

for relation in my_relations:
    generate_positive_answer_pairs(patterns_dict[relation], triples_dict[relation], relation)
for relation in my_relations:
    generate_negative_answer_pairs(patterns_dict[relation], triples_dict[relation], relation)