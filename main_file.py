import time
import telepot
import pprint
import json
from itertools import ifilter
from telepot.loop import MessageLoop
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton
import server as s
from database import Database
from babelnet import BabelNet
from neural_network import NeuralNetwork
from hitajutilities import sentence_subjects,\
    sentence_nouns, \
    filter_by_relation,\
    question_to_ask, \
    relation_to_ask, \
    extract_answer_concept, filter_yes_no
from sentence_similarity import symmetric_sentence_similarity
from constants import BOT_TOKEN

network = NeuralNetwork('/home/dorjan/Desktop/Word2vec/')
network.load_vectors()
db = Database()
babelnet = BabelNet()
domains = s.get_babel_domains()

'''
    Telegram and bot handling base skeleton is taken from telepot documentations and forums online about telegram bots
'''


class TelegramBot:

    def __init__(self):
        self.interaction_domain = -1
        self.interaction_direction = -1
        self.user_question = ""
        self.user_answer = ""
        self.lemma = ""
        self.relation = ""
        self.bot_question = ""

    def get_domain(self):
        return self.interaction_domain

    def set_domain(self, domain):
        self.interaction_domain = domain

    def get_interaction_direction(self):
        return self.interaction_direction

    def set_interaction_direction(self, mode):
        self.interaction_direction = mode

    def get_user_question(self):
        return self.user_question

    def set_user_question(self, query):
        self.user_question = query

    def get_user_answer(self):
        return self.user_answer

    def set_user_answer(self, user_answer):
        self.user_answer = user_answer
        
    def get_lemma(self):
        return self.lemma

    def set_lemma(self, lemma):
        self.lemma = lemma

    def get_relation(self):
        return self.relation

    def set_relation(self, rel):
        self.relation = rel

    def get_bot_question(self):
        return self.bot_question

    def set_bot_question(self, bot_question):
        self.bot_question = bot_question

    def handle(self, msg):

        content_type, chat_type, chat_id = telepot.glance(msg)

        if self.get_domain() == -1:
            random_domains = s.get_five_random_domains(domains)
            keyboard = InlineKeyboardMarkup(inline_keyboard=[[
                InlineKeyboardButton(text=str(random_domains[0][1]), callback_data=str(random_domains[0][1]).strip()),
                InlineKeyboardButton(text=str(random_domains[1][1]), callback_data=str(random_domains[1][1]).strip())],
                [InlineKeyboardButton(text=str(random_domains[2][1]), callback_data=str(random_domains[2][1]).strip()),
                 InlineKeyboardButton(text=str(random_domains[3][1]), callback_data=str(random_domains[3][1]).strip())],
                 [InlineKeyboardButton(text=str(random_domains[4][1]), callback_data=str(random_domains[4][1]).strip()),]])
            if self.get_domain() == -1:
                if content_type == 'text':
                    bot.sendMessage(chat_id, "Please select a domain to talk about:", reply_markup=keyboard)

        elif self.get_user_question() == "" and self.get_interaction_direction()==21:

            if content_type == 'text':
                query_data = msg['text']
                # rel = network.predict_relation(query_data)
                rel = network.get_rel_w2v(query_data)
                x = sentence_nouns(query_data.strip("?"))
                print x
                db_results = db.search_full_text(x)
                key_val = []
                key_val.append(rel)
                print("Relation predicted  ", rel)
                d = filter_by_relation(key_val, db_results)
                print("length of filtered by relation", len(d))
                d1 = filter_yes_no(d)
                print("length of filtered by yes no", len(d1))
                new_list = list()
                for item in d1:
                    data = dict()
                    sim_coeff = symmetric_sentence_similarity(query_data, item['question'])
                    data['answer'] = item['answer']
                    data['question'] = item['question']
                    data['similarity'] = sim_coeff
                    new_list.append(data)
                if len(d1) != 0:
                    k = sorted(new_list, key=lambda k: k['similarity'], reverse=True)
                    print(k[0]['question'], k[0]['answer'], k[0]['similarity'])
                    message = k[0]['answer']
                else:
                    message = "No answer was found"
                bot.sendMessage(chat_id, message)
                self.set_domain(-1)
                self.set_interaction_direction(-1)
                self.set_user_question("")

        elif self.get_user_answer() == "" and self.get_interaction_direction()==22:
            if content_type == 'text':
                query_data = msg['text']
                c2 = extract_answer_concept(self.get_lemma(), self.get_relation(), query_data)
                print("c2 is :------------->>>> ", c2)
                new_record = dict()
                new_record['question'] = self.get_bot_question()
                new_record['answer'] = self.get_user_answer()
                new_record['c1'] = self.get_lemma()
                new_record['context'] = self.get_user_answer()
                bc2 = BabelNet.get_babelnet_id(c2)
                if bc2 is not "":
                    concept2 = c2+"::"+bc2
                else:
                    concept2 = c2
                new_record['c2'] = concept2
                new_record['domains'] = self.get_domain()
                new_record['relation'] = self.get_relation()

                add_result = s.insert_single_item(json.dumps(new_record))
                print ("Server response: " , add_result)

                bot.sendMessage(chat_id, "Ok I will take note of that, If you need me I wll be here.")
                self.set_domain(-1)
                self.set_interaction_direction(-1)
                self.set_user_answer("")

    def on_callback_query(self, msg):
        query_id, from_id, query_data = telepot.glance(msg, flavor='callback_query')

        if self.get_domain() == -1:
            print('--->>>> ', query_id, from_id, query_data)
            self.set_domain(query_data)
            self.set_interaction_direction(-1)
        elif self.get_interaction_direction() == -1:
            print('--->>>> ', query_id, from_id, query_data)
            self.set_interaction_direction(int(query_data))
            if int(self.get_interaction_direction()) == 21:
                mode = "Ok go ahead and ask me something:"
                bot.sendMessage(from_id, mode)
            else:
                mode = "You have choosen: Enriching direction in "+str(self.get_domain())+" domain"
                bot.sendMessage(from_id, mode)
                x = babelnet.random_babelnet_id_in_domain(self.get_domain())
                print(x)
                lemmas = babelnet.db_search_terms(x)
                while lemmas == 0:
                    x = babelnet.random_babelnet_id_in_domain(self.get_domain())
                    print(x)
                    lemmas = babelnet.db_search_terms(x)
                pprint.pprint(lemmas)
                dori = list()
                res = 0
                for lemma in lemmas:
                    g = db.search_by_field('c1', lemma)
                    dori.append(g)
                    res += len(g)

                if res > 0:
                    c = relation_to_ask(dori, babelnet.get_domain_relations())
                    print(c)
                    d, l = question_to_ask(c, lemmas[0], babelnet.get_relation_patterns(), babelnet.get_domain_relations(), self.get_domain())
                else:
                    c = 0
                    d, l = question_to_ask(c, lemmas[0], babelnet.get_relation_patterns(), babelnet.get_domain_relations(), self.get_domain())

                self.set_bot_question(d)
                self.set_lemma(lemmas[0])
                self.set_relation(l)

                bot.sendMessage(from_id, d)

        if self.get_interaction_direction() == -1:
            keyboard = InlineKeyboardMarkup(inline_keyboard=[[
                InlineKeyboardButton(text='You ask, I answer', callback_data='21'),
                InlineKeyboardButton(text='I ask, you help me learn', callback_data='22')
            ]])
            bot.sendMessage(from_id, "Select direction:", reply_markup=keyboard)


bot = telepot.Bot(BOT_TOKEN)
carbon_bot = TelegramBot()
MessageLoop(bot, {'chat': carbon_bot.handle, 'callback_query': carbon_bot.on_callback_query}).run_as_thread()
print('Listening ...')
while 1:
    time.sleep(10)

