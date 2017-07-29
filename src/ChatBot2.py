import aiml,os, nltk, re, json
from NamedEntitiesStanford import NamedEntitiesStanford
from naiveBayesClassifier import tag_prob
from getInfo import GetSubCategory
from CityName import CityName
from UserName import UserName
from spell_check import correct_Sent
import datetime
from logger import logger
from customer import Lookup
import requests, uuid
from sleekxmpp import ClientXMPP

class ChatBot2(object):

    def __init__(self, settings, client_xmpp):
        self.client_xmpp = client_xmpp
        self.settings = settings
        self.form_cat_list = ["beauty-services", "Laundry", "travel-and-tickets", "diagnostics"]
        self.dyn_forms = self.init_dyn_forms(settings)
        self.form_sub_cat_dict = {
             "travel-and-tickets" : [
                 {
                    "tokens" : ["flight", "aeroplane", "aircraft"],
                    "sub-category" : "travel-and-tickets/flight"
                 },
                 {
                    "tokens" : ["bus", "train", "buses", "trains"],
                    "sub-category" : "travel-and-tickets/bus-train"
                 }
            ],
            "beauty-services" : [
                {
                    "tokens" : ["threading", "eyebrow"],
                    "sub-category" : "beauty-services/threading"
                },
                {
                    "tokens" : ["facial", "facials"],
                    "sub-category" : "beauty-services/facials"
                },
                {
                    "tokens" : ["manicur", "menicur", "manicure", "menicure"],
                    "sub-category" : "beauty-services/manicure"
                },
                {
                    "tokens" : ["polish", "body"],
                    "sub-category" : "beauty-services/body-polish"
                },
                {
                    "tokens" : ["makeup", "make-up", "makup"],
                    "sub-category" : "beauty-services/makeup"
                },
                {
                    "tokens" : ["threading", "eyebrow"],
                    "sub-category" : "beauty-services/hair-services"
                },
                {
                    "tokens" : ["pedicure", "padicure", "pedicur", "padicur"],
                    "sub-category" : "beauty-services/padicure"
                },
                {
                    "tokens" : ["massage", "masag"],
                    "sub-category" : "beauty-services/massage"
                },
                {
                    "tokens" : ["tan", "detan"],
                    "sub-category" : "beauty-services/detan"
                },
                {
                    "tokens" : ["wax", "waxing"],
                    "sub-category" : "beauty-services/waxing"
                }
            ],
            "laundry" : [
                {
                    "tokens" : ["laundry", "clothes", "cloth", "bangalore"],
                    "sub-category" : "laundry"
                },
                {
                    "tokens" : ["laundry", "clothes", "cloth", "hyderabad"],
                    "sub-category" : "laundry"
                },
            ],
            "diagnostics" : [
                {
                    "tokens" : ["diagnostic", "diagnostics", "medical", "tests"],
                    "sub-category" : "diagnostics"
                }
            ]
        }

        self.intent_dict = {'meat':'provide','food and beverages':'want','Laundry':'clean',
                            'utility-and-bills':'recharge','grocery-and gourmet-food':'deliver',
                            'travel-and-tickets':'book', 'home-services': 'provide',
                            'beauty-services':'deliver'}
        self.category_score = {'meat':0.7,'food and beverages':0.9,'Laundry':0.5,'utility-and-bills':0.45,
                               'grocery-and gourmet-food':0.5, 'travel-and-tickets':0.7,
                               'home-services': 0.5, 'beauty-services':0.8}
        self.kernel = self.initiate_bot_brain()

        self.order_dict = {'routing':False, 'intents' : [], 'Username':'', 'name':''}
        self.status_dict = ['routing', 'name', 'intent', 'welcome']

        self.st_time = 0
        self.end_time = datetime.datetime.now()
        self.allowed_time_reset = 30
        self.chat_id = -1
        self.c= [0]*100 #A counter to avoid repetitions

    def init_dyn_forms(self, settings):
        forms_url = settings["form_url"]
        resp = requests.get(forms_url, headers=settings["http_header"])
        if resp.status_code == 200:
            forms_resp = json.loads(resp.text)
            return forms_resp["results"]
        else:
            return []

    def get_order_dict(self):
        return self.order_dict

    def get_chat_id(self):
        return self.chat_id

    def init_chat_id(self, msg):
        if self.chat_id == -1:
            msg_str = str(msg)
            msg_tokens = msg_str.split()
            logger.info("Extracting chat id...")
            for token in msg_tokens:
                if "chat_thread" in token:
                    self.chat_id = token.split("=")[1][1:-1]

    def get_chat(self):
        chat_url = self.settings["chat_url"] + str(self.chat_id) + "/"
        resp = requests.get(chat_url, headers=self.settings["http_header"])
        if resp.status_code == 200:
            return json.loads(resp.text)
        else:
            return None

    def check_owner(self):
        ret = False
        resp_json = self.get_chat()
        logger.info(resp_json)
        logger.info(self.settings["bot_id"])
        if resp_json:
            owner = resp_json["agent"]
            if owner == self.settings["bot_id"]:
                ret = True
        return ret

    def processMsg(self, msg, cl):
        self.init_chat_id(msg)
        response = ""
        bye_msg = "Bye"

        # check if this chat is owned by me... :)
        if not self.check_owner():
            logger.info("Jarvis2 not owner of this chat anymore! Not processing this message...")
            return response, self.order_dict, self.chat_id

        # Reset logic. If user does not get back in 30 mins, we reset the info
        # that was captured and restart the whole conversation
        self.st_time = datetime.datetime.now()
        elapsed = self.end_time - self.st_time
        if elapsed > datetime.timedelta(minutes=self.allowed_time_reset):
            # reset
            self.reset_order()

        if msg['type'] in ('chat', 'normal'):
            message = msg['body']
            if "_mt_cmmd" not in message:
                logger.info("Text message request: " + message)

                cust_id = -1 # Default value
                if self.order_dict['Username'] == '':
                    self.order_dict['Username'], self.order_dict['Cityname'], email, cust_id = \
                        Lookup(self.settings).lookup(msg)
                    if self.order_dict['Username']:
                        self.status_dict.remove('name')

                if (self.check_if_close(message)):
                    response = bye_msg
                else:
                    response = self.process(cl, msg['body'], cust_id)
                    if self.order_dict['routing'] and self.status_dict==[]:
                        self.send_message(msg['from'], response)
                        # Check if a form can be sent before routing
                        form = self.check_form()
                        if form and self.check_device():
                            logger.info("Sending form")
                            self.reply(msg, form)
                        # Call routing function
                        logger.info("Routing to human agent now...")
                        response = bye_msg
                    else:
                        self.reply(msg, response)
            else:
                logger.info("Ignoring assignment message.")
        self.end_time = datetime.datetime.now()
        return response, self.order_dict, self.chat_id

    def send_message(self, to_user, body, msubject=None, mtype=None,
                     mhtml=None, mfrom=None, mnick=None):
        """
        <message from="9591418090@stage-c.magictiger.com/mtx-android" msg_type="10" chat_thread="941" id="purple58e460b8" to="subramanian@stage-c.magictiger.com/matrix" sent_on="1450200033598" type="chat" xml:lang="en" mt_routed="true"><body>Dumbbot</body><markable xmlns="urn:xmpp:chat-markers:0" /></message>
        """
        logger.info('Trying to send_message')
        msg_xml = self.client_xmpp.make_message(mto=to_user, mbody=body, msubject=msubject, mtype=mtype, mhtml=mhtml, mfrom=mfrom, mnick=mnick)
        msg_xml.xml.set('from', str(self.client_xmpp.boundjid))
        msg_xml.xml.set('id', str(uuid.uuid4()))
        msg_xml.xml.set('type',"chat")
        msg_xml.xml.set('mt_routed',"false")
        logger.info(msg_xml)
        resp = msg_xml.send()
        logger.info(resp)
        return msg_xml

    def check_form(self):
        form = {}
        if self.check_device():
            # Fit case to send form. Now check if category is suitable
            intents = self.order_dict["intents"]
            if intents != []:
                intent = intents[0]
                cat = intent["category"]
                sub_cat = intent["subCategory"]
                if cat["type"] in self.form_cat_list:
                    sc = ""
                    # Check if sub-category is available
                    sub_cat_list = self.form_sub_cat_dict[cat["type"]]

                    # Tokenize the sub-cat string recved in intent dict
                    tokens = nltk.word_tokenize(sub_cat["type"])

                    for tok in tokens:
                        sc_url = self.check_match(tok, sub_cat_list)
                        logger.info("Recvd sub-cat " + str(sc_url))
                        if sc_url:
                            form = self.search_scat(sc_url)
                            break
        return form

    def search_scat(self, sc_url):
        ret_form = {}
        for form in self.dyn_forms:
            form_cat_url = form["category"]
            logger.info(form_cat_url)
            if sc_url == form_cat_url:
                logger.info(sc_url)
                ret_form = form["form_json"]
                logger.info(ret_form)
                break
        return ret_form

    def check_match(self, tok, sub_cat_list):
        sc_url = ""
        for scat in sub_cat_list:
            scat_tokens = scat["tokens"]
            if tok in scat_tokens:
                sc_url = scat["sub-category"]
                break
        return sc_url

    def check_device(self):
        # At first get the device information - android, ios?
        chat_resp = self.get_chat()
        if chat_resp:
            medium = chat_resp["medium"]
            if medium == "mobile":
                return True
            else:
                return False

    def send_form(self):
        pass

    def reply(self, msg, response):
        msg.xml.set('mt_routed','false')
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
                        return k.respond(name + ' welcome done' + '  order complete ' + str(self.c[3]))
                    else:
                        self.c[4]+=1
                        return k.respond(name + ' welcome done' + '  routing unknown ' + str(self.c[4]))
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

    def updateEmailInDb(self, Email, cust_id):
        url = self.settings["profiles_url"] + str(cust_id) + "/emails/"
        email_data = {"email" : Email, "tag" : "Other"}
        requests.post(url, data=email_data, headers=self.settings["http_header"])

    def generateAimlQuery(self, query):
        k = self.initiate_bot_brain()
        return k.respond(query)

    def process(self, cl, msg, cust_id):
        #Email = self.getEmail(msg)
        #message = self.removeEntities(msg,[Email])
        message = msg

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
            l = [ i for i in self.c if i==2]
            if len(l)>=1:
                logger.info("Jarvis2 done with this this guy!")
                self.order_dict["routing"] = True
                self.status_dict = []
                return self.generateAimlQuery('direct him to the agent')
            else:
                return response
        else:
            self.generateQuery()
            print self.status_dict
            return self.generateAimlQuery('direct him to the agent')