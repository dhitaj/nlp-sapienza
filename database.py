import pymongo
import json


class Database:

    def __init__(self):
        self.client = pymongo.MongoClient('localhost:27017')
        self.db = self.client['server']
        self.collection = self.db["server_collection"]
        self.collection.create_index([('question', 'text'),
                             ('relation', 'text'),
                             ('c1', 'text')])
        # self.collection.drop_indexes()

    def search_by_field(self, field_name, search_value):
        search_result = []
        result = self.collection.find({field_name: search_value})
        for document in result:
            data_dict = dict()
            data_dict['question'] = document['question']
            data_dict['relation'] = document['relation']
            data_dict['c2'] = document['c2']
            data_dict['c1'] = document['c1']
            data_dict['answer'] = document['answer']
            data_dict['domain'] = document['domains']
            search_result.append(data_dict)
        
        return search_result
    
    def search_full_text(self, list_of_keywords):
        search_result = []
        for key in list_of_keywords:
            x = self.collection.find({"$text": {"$search": key}})
            for document in x:
                data_dict = dict()
                data_dict['question'] = document['question']
                data_dict['relation'] = document['relation']
                data_dict['c2'] = document['c2']
                data_dict['c1'] = document['c1']
                data_dict['answer'] = document['answer']
                data_dict['domain'] = document['domains']
                search_result.append(data_dict)
        
        return search_result
    
    def add_new_records(self, new_records):
        with open('data/'+new_records, 'r') as infile:
            for line in infile:
                x = json.loads(line)
                for line2 in x:
                    self.collection.insert(line2)
        return 0
