__author__ = 'dorjan'
from constants import SERVER
from constants import BABELFY_TOKEN
import urllib2
import urllib
import random as rand
import requests

'''
    The methods below serve to communicate with the Knowledge Base
'''


def get_babel_domains():
    domains_url = "http://lcl.uniroma1.it/babeldomains/domain_list.txt"
    f = urllib.urlopen(domains_url)
    domains = f.readlines()
    return domains

# method expects a json object
def insert_single_item(item):
    response = requests.post(SERVER+'add_item?key='+BABELFY_TOKEN, data=item)
    return response  # check response status if equals 200


def insert_many_items(items):
    response = requests.post(SERVER+'add_item?key='+BABELFY_TOKEN, data=items)
    return response


def knowledge_base_records():
    # check how many records are in the Knowledge Base
    amount = SERVER + 'items_number_from?id=0&key=' + BABELFY_TOKEN
    req = urllib2.Request(amount)

    fd = urllib2.urlopen(req)
    resp = fd.read()
    nr = int(resp)

    i = 0
    # get all the data in chunks of 5000 and populate a file, after that this fileis used to populate the database
    filehandle = open('data/full_server_dump.txt', 'a')
    while i <= nr:

        url = SERVER + 'items_from?id=' + str(i) + '&key=' + BABELFY_TOKEN
        req = urllib2.Request(url)
        fd = urllib2.urlopen(req)
        resp = fd.read()
        filehandle.write(resp)
        filehandle.write('\n')
        i += 5000
    filehandle.close()


def get_five_random_domains(babel_domains):
    random_indices = rand.sample(range(0,len(babel_domains)-1), 5)
    sample_domains = list()
    for i in random_indices:
        sample_domains.append((i, babel_domains[i]))
    return sample_domains
