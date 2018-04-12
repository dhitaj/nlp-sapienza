from database import Database
from babelnet import BabelNet
from server import knowledge_base_records

'''
    Please insert the babedomains_babelnet.txt file under the data directory before running this file
'''

BabelNet.babelnet_ids_to_babelnet_domain_dictionary()
knowledge_base_records()
db = Database()
db.add_new_records('full_server_dump.txt')
