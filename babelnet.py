__author__ = 'dorjan'
import urllib2
import urllib
import json
import gzip
from StringIO import StringIO
from constants import BABELNET_TOKEN
import random


class BabelNet:

    def __init__(self):
        self.babelnet_domain_vectors = self.load_babelnet_domains_dict('data/babeldomains_dict.txt')
        self.domain_rels = self.domain_relations()
        self.relation_question_patterns = self.relation_questions()

    @staticmethod
    def get_babelnet_lemma_by_babelnet_id(id):
        params = {
            'id': id,
            'key': BABELNET_TOKEN
        }
        service_url = 'https://babelnet.io/v4/getSynset'
        url = service_url + '?' + urllib.urlencode(params)
        request = urllib2.Request(url)
        request.add_header('Accept-encoding', 'gzip')
        response = urllib2.urlopen(request)
        x = 0
        lemma = ''
        senses=[]
        if response.info().get('Content-Encoding') == 'gzip':
            buf = StringIO(response.read())
            f = gzip.GzipFile(fileobj=buf)
            data = json.loads(f.read())
            senses = data['senses']

        try:
            for result in senses:
                lemma = result.get('lemma')
                break
            x = lemma.encode('utf-8')
        except:
            x = 0
        return x

    @staticmethod
    def get_babelnet_id(word):

        service_url = 'https://babelnet.io/v4/getSynsetIds'

        word = word
        lang = 'EN'
        key = BABELNET_TOKEN

        params = {
            'word': word,
            'langs': lang,
            'key': key
        }

        url = service_url + '?' + urllib.urlencode(params)
        request = urllib2.Request(url)
        request.add_header('Accept-encoding', 'gzip')
        response = urllib2.urlopen(request)
        b_id = ""
        if response.info().get('Content-Encoding') == 'gzip':
            buf = StringIO(response.read())
            f = gzip.GzipFile(fileobj=buf)
            data = json.loads(f.read())
            for result in data:
                b_id = result['id']
                break

        return b_id


    def db_search_terms(self, babelnet_id):
        flag = False
        lemma = None
        lemma = self.get_babelnet_lemma_by_babelnet_id(babelnet_id)
        if lemma is '':
            return 0
        new_lemma = lemma.replace("_", " ")
        search_terms = list()
        search_terms.append(new_lemma)
        search_terms.append(new_lemma+'::')
        search_terms.append(new_lemma+'::'+babelnet_id)
        return search_terms

    @staticmethod
    def load_babelnet_domains_dict(filepath):
        k = None
        f = open(filepath)
        for line in f:
            k = json.loads(line)
        return k

    @staticmethod
    def babelnet_ids_to_babelnet_domain_dictionary():
        data_dict = dict()
        with open('data/babeldomains_babelnet.txt', 'r') as filehandle:
            for line in filehandle:
                l = line.split('\t')
                babelnet_id = l[0].strip()
                domain = l[1].strip()
                if data_dict.has_key(domain):
                    data_dict[domain].append(babelnet_id)
                else:
                    data_dict[domain] = [babelnet_id, ]

        filehandle2 = open('data/babeldomains_dict.txt', 'w')
        json_dict = json.dumps(data_dict)
        filehandle2.write(json_dict)
        filehandle2.close()

    def get_babelnet_domains_dict(self):
        return self.babelnet_domain_vectors

    def get_domain_relations(self):
            return self.domain_rels

    def get_relation_patterns(self):
            return self.relation_question_patterns

    def random_babelnet_id_in_domain(self, domain):
        babelnet_domains_dict = self.get_babelnet_domains_dict()
        babelnet_ids = babelnet_domains_dict[domain]
        index = random.randint(0, len(babelnet_ids)-1)
        return babelnet_ids[index]

    @staticmethod
    def domain_relations():
        from collections import defaultdict
        domain_relations_dict = defaultdict(list)
        filehandle = open('data/domains_to_relations.tsv')
        for line in filehandle:
            a = line.split('\t')
            domain = a[0].strip()
            for x in range(1, len(a)-1):
                domain_relations_dict[domain].append(a[x].strip())

        return domain_relations_dict

    @staticmethod
    def relation_questions():
        from collections import defaultdict
        relations_dict = defaultdict(list)
        filehandle = open('data/patterns.tsv')
        for line in filehandle:
            a = line.split('\t')
            relation = a[1].strip()
            if relations_dict.has_key(relation):
                relations_dict[relation].append(a[0])
            else:
                relations_dict[relation] = [a[0], ]
        return relations_dict
