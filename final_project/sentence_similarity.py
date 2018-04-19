__author__ = 'dorjan'
from nltk import word_tokenize, pos_tag
from nltk.corpus import wordnet as wn

#   The sentence similarity algorithm was taken online as suggested by the paper:
#   'Corpus-based and Knowledge-based Measures of Text Semantic Similarity' by Michaela et al
#   Link to paper: ----> https://www.aaai.org/Papers/AAAI/2006/AAAI06-123.pdf


def penn_to_wn(tag):
    if tag.startswith('N'):
        return 'n'
    if tag.startswith('V'):
        return 'v'
    if tag.startswith('J'):
        return 'a'
    if tag.startswith('R'):
        return 'r'
    return None


def tagged_to_synset(word, tag):
    wn_tag = penn_to_wn(tag)
    if wn_tag is None:
        return None
    try:
        return wn.synsets(word, wn_tag)[0]
    except:
        return None


def sentence_similarity(sentence1, sentence2):
    sentence1 = pos_tag(word_tokenize(sentence1))
    sentence2 = pos_tag(word_tokenize(sentence2))
    synsets1 = [tagged_to_synset(*tagged_word) for tagged_word in sentence1]
    synsets2 = [tagged_to_synset(*tagged_word) for tagged_word in sentence2]
    synsets1 = [ss for ss in synsets1 if ss]
    synsets2 = [ss for ss in synsets2 if ss]
    score, count = 0.0, 0
    for synset in synsets1:
        best_score = max([synset.path_similarity(ss) for ss in synsets2])
        if best_score is not None:
            score += best_score
            count += 1
    if count != 0:
        score /= count
    else:
        score = 0
    return score


def symmetric_sentence_similarity(sentence1, sentence2):
    return (sentence_similarity(sentence1, sentence2) + sentence_similarity(sentence2, sentence1)) / 2
