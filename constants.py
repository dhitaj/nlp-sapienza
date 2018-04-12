__author__ = 'dorjan'

BOT_TOKEN = ""

BABELFY_TOKEN = ""

BABELNET_TOKEN = ""

SERVER = ''

RELATIONS = ['ACTIVITY', 'PART', 'PLACE',
             'SIZE', 'GENERALIZATION',
             'TIME', 'HOW_TO_USE', 'SPECIALIZATION',
             'MATERIAL', 'PURPOSE', 'TASTE', 'SOUND',
             'SIMILARITY', 'COLOR', 'SHAPE', 'SMELL']

RELATION_POS_TAGS = {
    'ACTIVITY': ['VB', 'VBD', 'VBP'],
    'PART': ['NN', 'NNP', 'NNS'],
    'PLACE': ['NN', 'NNP', 'NNS'],
    'SIZE': ['NN', 'NNP', 'NNS'],
    'GENERALIZATION': ['NN', 'NNP', 'NNS'],
    'TIME': ['NN', 'NNP', 'NNS'],
    'HOW_TO_USE': ['VB', 'VBD', 'VBP'],
    'SPECIALIZATION': ['NN', 'NNP', 'NNS'],
    'MATERIAL': ['NN', 'NNP', 'NNS'],
    'PURPOSE': ['VB', 'VBD', 'VBP'],
    'TASTE': ['JJ', 'JJR', 'JJS'],
    'SOUND': ['JJ', 'JJR', 'JJS'],
    'SIMILARITY': ['NN', 'NNP', 'NNS'],
    'COLOR': ['JJ', 'JJR', 'JJS', 'VBN'],
    'SHAPE': ['JJ', 'JJR', 'JJS'],
    'SMELL': ['JJ', 'JJR', 'JJS']
}
