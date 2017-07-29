import aiml,os, nltk, re
from NamedEntitiesStanford import NamedEntitiesStanford
from naiveBayesClassifier import tag_prob
from getInfo import GetSubCategory
from CityName import CityName
from UserName import UserName
from spell_check import correct_Sent
import datetime
from logger import logger
from customer import Lookup
import requests

class ChatBot2:

    def __init__(self):
        self.intent_dict = {'meat':'provide','food and beverages':'want','Laundry':'clean','utility-and-bills':'recharge','grocery-and gourmet-food':'deliver', 'travel-and-tickets':'book', 'home-services': 'provide', 'beauty-services':'deliver'}
        self.category_score = {'meat':0.7,'food and beverages':0.9,'Laundry':0.5,'utility-and-bills':0.45,'grocery-and gourmet-food':0.5, 'travel-and-tickets':0.7, 'home-services': 0.5, 'beauty-services':0.8}
        self.kernel = self.initiate_bot_brain()

        self.order_dict = {'routing':False, 'intents' : [], 'Username':'', 'name':''}
        self.status_dict = ['routing', 'name', 'intent', 'welcome']

        self.st_time = 0
        self.end_time = datetime.datetime.now()
        self.allowed_time_reset = 30
        self.chat_id = -1
        self.profiles_url = "https://stage-api.magictiger.com/profiles/consumers/"
        self.c= [0]*100 #A counter to avoid repetitions
        self.state = {'initial':['routing', 'name', 'intent', 'welcome'],'present':self.status_dict,'past':[]}
        

    def get_order_dict(self):
        return self.order_dict

    def get_chat_id(self):
        return self.chat_id

    def update_name(self, name):
        pass

    def update_locn(self, location, cust_id):
        header = {
            "Authorization": "c28aab40-d62c-4386-8d90-9984d331d519",
            "Content-Type": "application/json"
        }
        # Post locations to locations DB
        prof_location_url = self.profiles_url + "/" + str(cust_id) + "/locations/"
        requests.post(prof_location_url, data=location, headers=header)

    def processMsg(self, msg, cl):
        bye_msg = "Thanks for using MagicTiger. Bye!"

        # Reset logic. If user does not get back in 30 mins, we reset the info
        # that was captured and restart the whole conversation
        self.st_time = datetime.datetime.now()
        elapsed = self.end_time - self.st_time
        if elapsed > datetime.timedelta(minutes=self.allowed_time_reset):
            # reset
            self.reset_order()

        response = ""
        if msg['type'] in ('chat', 'normal'):
            message = msg['body']
            if "_mt_cmmd" not in message:
                logger.info("Text message request: " + message)

                if self.chat_id == -1:
                    msg_str = str(msg)
                    msg_tokens = msg_str.split()
                    logger.info("Extracting chat id...")
                    for token in msg_tokens:
                        if "chat_thread" in token:
                            self.chat_id = token.split("=")[1][1:-1]

                if self.order_dict['Username'] == '':
                    self.order_dict['Username'], self.order_dict['Cityname'], cust_id = Lookup().lookup(msg)
                    if self.order_dict['Username']:
                        self.update_name(self.order_dict['Username'])
                    if self.order_dict['Cityname']:
                        self.update_locn(self.order_dict['Cityname'], cust_id)

                if (self.check_if_close(message)):
                    response = bye_msg
                else:
                    response = self.process(cl, msg['body'])
                    print response
                    if self.order_dict['routing'] and self.status_dict==[]:
                        # Call routing function
                        logger.info("Routing to human agent now...")
                        self.reply(msg, response)
                        response = bye_msg
                    else:
                        self.reply(msg, response)
            else:
                logger.info("Ignoring assignment message.")
        self.end_time = datetime.datetime.now()
        print response, self.order_dict, self.chat_id
        return response, self.order_dict, self.chat_id

    def reply(self, msg, response):
        print response
        msg.xml.set('mt_routed','false')
        print msg
        #import pdb; pdb.set_trace()
        msg.reply(response).send()

    def check_if_close(self, message):
        if (message.lower() == "bye") or (message.lower() == "goodbye"):
            return True
        else:
            return False

    def reset_order(self):
        self.order_dict = {'routing':False, 'intents' : [], 'Username':'', 'Cityname':''}

    def initiate_bot_brain(self):
        k = aiml.Kernel()

        #Load bot's brain
        if os.path.isfile("bot_brain.brn"):
            k.bootstrap(brainFile = "bot_brain.brn")
        else:
            k.bootstrap(learnFiles = "std-startup.xml", commands = "load aiml b")
            k.saveBrain("bot_brain.brn")
        return k

    def checkForOrderCompletion(self,d):
        if self.empty_dict(d,0)==0:
            return True
        else:
            return False

    def empty_dict(self, d, value):
      for k, v in d.iteritems():
        if isinstance(v, dict):
          value = value + self.empty_dict(v, 0)
        if isinstance(v, list):
            for item in v:
                value = value + self.empty_dict(item,0)
        else:
          if v=='':
              value = value+1
          if v==False:
              value = value + 1

      return value
    def completeOrder(self,d,session):
        for key in d:
            if d[key]=='' and key in session:
                d[key]=session[key]
        return d

    def remove_stopwords(self, sent):
        stopwords = nltk.corpus.stopwords.words('english')
        l = [i for i in sent.split() if i not in stopwords]
        return ' '.join(l)

    def tokenize_only(self,text):
        # first tokenize by sentence, then by word to ensure that punctuation is caught as it's own token
        tokens = [word.lower() for sent in nltk.sent_tokenize(text) for word in nltk.word_tokenize(sent)]
        filtered_tokens = []
        # filter out any tokens not containing letters (e.g., numeric tokens, raw punctuation)
        for token in tokens:
            if re.search('[a-zA-Z]', token):
                filtered_tokens.append(token)
        return ' '.join(filtered_tokens)

    def checkCityName(self, Name_city):
        cityname = CityName()
        for names in Name_city:
            if cityname.CheckCityName(names):
                return True
        return False

    def getPlaceNamefromNE(self, Names):
        if len(Names)>1:
            Username = Names[0:len(Names)-1]
            Cityname = Names[-1]
            if self.checkCityName(Username):
                if len(Names)>1:
                    Username = Names[1:]
                else:
                    Username =['']
                Cityname = Names[0]
            else:
                if self.checkCityName([Cityname])==False:
                    Username = ' '.join(Names)
                    Cityname = ''
            if type(Username)==list:
                if len(Username)>1:
                    Names = ' '.join(Username)
                elif len(Username)==1:
                    Names = Username[0]
                else:
                    Names = Username
            else:
                Names = Username
            Place = Cityname
        if len(Names)==1:
            Username = Names[0]
            Cityname = ''
            if self.checkCityName(Username):
                Cityname = Names[0]
                Username = ''
            Names = Username
            Place = Cityname
        return Names, Place

    def getPlaceName(self,message):
        nes = NamedEntitiesStanford()
        u = UserName()
        Place,_,Names = nes.GetEntities(message)
        if Place==[] and Names!=[]:
            Names, Place = self.getPlaceNamefromNE(Names)
        elif Place!=[] and Names==[]:
            Place, Names = self.getPlaceNamefromNE(Place)
            if Names=='':
                Names = ' '.join([i for i in message.split() if u.CheckPersonName(i)])

        else:
            if Names == []:
                Names = ''
            else:
                if len(Names)>1:
                    Names = ' '.join(Names)
                else:
                    Names = Names[0]
            if Place == []:
                Place = ''
            else:
                if len(Place)>1:
                    Place = ' '.join(Place)
                else:
                    Place = Place[0]
        return Names, Place

    def findSubcategory(self,message,category,score):
        try:
            subCategory,intent = GetSubCategory(message)
            if subCategory=='':
                subCategory=message
            if score>0.8 and intent=='':
                intent = self.intent_dict[category]
            #print subCategory,intent
        except UnboundLocalError:
            subCategory = message
            intent = self.intent_dict[category]
            #print subCategory,intent
        return subCategory, intent

    def removeEntities(self, message, entity_list):
        for item in entity_list:
            message = message.replace(item,'')
        return self.remove_stopwords(self.tokenize_only(message))

    def fillOrderList(self,Username,subCategory,intent,category,score):
        if not self.order_dict['Username']:
            self.order_dict['Username']=Username
        if intent!='':
            intent_dict = {'category':{'score': 0.0, 'type': ''},'subCategory': {'intent': '', 'type': ''}}
            intent_dict['category']['type']=category
            intent_dict['category']['score']=score
            intent_dict['subCategory']['type']=subCategory
            intent_dict['subCategory']['intent']=intent
            self.order_dict['intents'].append(intent_dict)

    def generateQuery(self):
        k = self.kernel
        intents = self.order_dict['intents']
        print "intent = " +  str(intents)

        name = self.order_dict['Username']
        #email = self.order_dict['email'].replace('.','')

#        if intents!=[] and 'intent' not in self.status_dict:
#            print "intent not null, inserting something"
#            self.status_dict.insert(1,'intent')

        if len(intents)>=1:
            self.order_dict['routing']=True

        routing = self.order_dict['routing']
        if intents:
            intent = intents[0]["subCategory"]["intent"]
        else:
            intent = ""

        if self.status_dict[-1]=='welcome':
            if 'welcome' in self.status_dict:
                self.status_dict.pop()
            if intent:
                if 'intent' in self.status_dict:
                    self.status_dict.pop()
                if name:
                    if 'name' in self.status_dict:
                        self.status_dict.pop()
                    if routing:
                        if 'routing' in self.status_dict:
                            self.status_dict.pop()
                        self.c[3]+=1
                        return k.respond(name + 'welcome done' + '  order complete ' + str(self.c[3]))
                    else:
                        self.c[4]+=1
                        return k.respond(name + 'welcome done' + '  routing unknown ' + str(self.c[4]))
                else:
                    self.c[5]+=1
                    return k.respond('welcome done' + '  name unknown routing unknown ' + str(self.c[5]))
            else:
                if name:
                    if 'name' in self.status_dict:
                        self.status_dict.remove('name')
                    if routing:
                        if 'routing' in self.status_dict:
                            self.status_dict.remove('routing')
                        self.c[7]+=1
                        return k.respond(name + ' welcome done' + '  intent unknown ' + str(self.c[7]))
                    else:
                        self.c[8]+=1
                        return k.respond(name + ' welcome done' + '  intent unknown routing unknown ' + str(self.c[8]))
                else:
                    if routing:
                        if 'routing' in self.status_dict:
                            self.status_dict.remove('routing')
                        self.c[9]+=1
                        return k.respond('welcome done' + '  intent name unknown ' + str(self.c[9]))
                    else:
                        self.c[10]+=1
                        return k.respond(' welcome done' + '  intent name unknown routing unknown ' + str(self.c[10]))
        elif self.status_dict[-1]=='intent':
            if intent:
                if 'intent' in self.status_dict:
                    self.status_dict.pop()
                if name:
                    if 'name' in self.status_dict:
                        self.status_dict.pop()
                    if routing:
                        if 'routing' in self.status_dict:
                            self.status_dict.pop()
                        self.c[13]+=1
                        return k.respond(name + ' order complete ' + str(self.c[13]))
                    else:
                        self.c[14]+=1
                        return k.respond(name + ' routing unknown ' + str(self.c[14]))
                else:
                    self.c[15]+=1
                    return k.respond(' name unknown routing unknown ' + str(self.c[15]))
            else:
                if name:
                    if 'name' in self.status_dict:
                        self.status_dict.remove('name')
                    if routing:
                        if 'routing' in self.status_dict:
                            self.status_dict.remove('routing')
                        self.c[17]+=1
                        return k.respond(name + '  intent unknown ' + str(self.c[17]))
                    else:
                        self.c[18]+=1
                        return k.respond(name + '  intent unknown routing unknown ' + str(self.c[18]))
                else:
                    if routing:
                        if 'routing' in self.status_dict:
                            self.status_dict.remove('routing')
                        self.c[19]+=1
                        return k.respond(' intent name unknown ' + str(self.c[19]))
                    else:
                        self.c[20]+=1
                        return k.respond('  intent name unknown routing unknown ' + str(self.c[20]))
        elif self.status_dict[-1]=='name':
            if name:
                if 'name' in self.status_dict:
                    self.status_dict.pop()
                if routing:
                    if 'routing' in self.status_dict:
                        self.status_dict.pop()
                    self.c[22]+=1
                    return k.respond(name + '  order complete ' + str(self.c[22]))
                else:
                    self.c[23]+=1
                    return k.respond(name + '  routing unknown ' + str(self.c[23]))
            else:
                if routing:
                    if 'routing' in self.status_dict:
                        self.status_dict.remove('routing')
                    self.c[24]+=1
                    return k.respond(' name unknown ' + str(self.c[24]))
                else:
                    self.c[25]+=1
                    return k.respond('  name unknown routing unknown ' + str(self.c[25]))
        elif self.status_dict[-1]=='routing':
            if routing:
                if 'routing' in self.status_dict:
                    self.status_dict.pop()
                self.c[26]+=1
                return k.respond(' order complete ' + str(self.c[26]))
            else:
                self.c[27]+=1
                return k.respond(' routing unknown ' + str(self.c[27]))
        elif self.status_dict[-1]=='name':
            if name:
                if 'name' in self.status_dict:
                    self.status_dict.pop()
                if routing:
                    if 'routing' in self.status_dict:
                        self.status_dict.pop()
                    self.c[22]+=1
                    return k.respond(name + '  order complete ' + str(self.c[22]))
                else:
                    self.c[23]+=1
                    return k.respond(name + '  routing unknown ' + str(self.c[23]))
            else:
                if routing:
                    if 'routing' in self.status_dict:
                        self.status_dict.remove('routing')
                    self.c[24]+=1
                    return k.respond(' name unknown ' + str(self.c[24]))
                else:
                    self.c[25]+=1
                    return k.respond('  name unknown routing unknown ' + str(self.c[25]))
        elif self.status_dict[-1]=='routing':
            if routing:
                if 'routing' in self.status_dict:
                    self.status_dict.pop()
                self.c[26]+=1
                return k.respond(' order complete ' + str(self.c[26]))
            else:
                self.c[27]+=1
                return k.respond(' routing unknown ' + str(self.c[27]))

    def getEmail(self,message):
        match = re.findall(r'[\w\.-]+@[\w\.-]+', message)
        if match:
            return match[0]
        else:
            return ''

    def generateAimlQuery(self, query):
        k = self.kernel
        return k.respond(query)
        
    def updateState(self):
        l = self.state['initial']
        r = self.status_dict
        self.state['past'] = [i for i in l if i not in r]
        
    def getNextState(self):
        return self.state['present'][-1]
        
    def getTransition(self):
        return self.state['past'][0], self.state['present'][-1]
        
    

    def process(self, cl, msg):
        #Email = self.getEmail(msg)
        #message = self.removeEntities(msg,[Email])
        message = correct_Sent(msg)

        Username, Placename = self.getPlaceName(message)
        category, score = tag_prob(message,cl)
        if self.removeEntities(message, [Username, Placename]) =='':
            subCategory, intent = '',''
        else:
            subCategory, intent = self.findSubcategory(self.removeEntities(message, [Username, Placename]),category,score)
        self.fillOrderList(Username,subCategory,intent,category,score)
        if not self.checkForOrderCompletion(self.order_dict):
            logger.info(intent)
            response = self.generateQuery() #intent has to be removed and adjusted with aiml reply
            print self.status_dict
            self.updateState()
            print self.state
            l = [ i for i in self.c if i==2]
            if len(l)>=1:
                return self.generateAimlQuery('direct him to the agent')
            else:
                return response
        else:
            self.generateQuery()
            print self.status_dict
            self.updateState()
            print self.state
            return self.generateAimlQuery('direct him to the agent')