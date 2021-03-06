# -*- coding: utf-8 -*-
"""
Created on Tue Jan 12 15:09:24 2016

@author: bibekbehera
"""

# -*- coding: utf-8 -*-
"""
Created on Tue Nov 10 10:58:10 2015

@author: bibekbehera
"""

from textblob import TextBlob
from textblob.np_extractors import ConllExtractor
from nltk.corpus import stopwords
from dateutil import parser
import sys
sys.path.insert(0,'../MBSP')
import mbsp as MBSP
import nltk,re, os, cPickle
from itertools import groupby
from CityName import CityName
from UserName import UserName
from NamedEntitiesStanford import NamedEntitiesStanford
from naiveBayesClassifier import tag_prob
from witX import witX

abs_path = os.path.dirname(os.path.abspath('__file__'))

class megamind():
    
    def __init__(self,cl):
        self.extractor = ConllExtractor()
        self.stopwords = nltk.corpus.stopwords.words('english')
        self.cityname = CityName()
        
        self.cl = cl
        self.w = witX()
        
        
    def validate(self,time_text):
        try:
            parser.parse(time_text)
        except ValueError:
            return 1

    def remove_stopwords(self,sent):
        l = [i for i in sent.split() if i.decode("unicode_escape") not in self.stopwords]
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
    
    def replaceChuncks(self, TEXT, chuncks):
        for item in chuncks:
            if item.replace('_',' ') in TEXT:
                TEXT = TEXT.replace(item.replace('_',' '), item)
        return TEXT
    
    def find_chunks(self, TEXT, time):
        blob = TextBlob(TEXT, np_extractor=self.extractor)
        
        chuncks = ['_'.join(i) for i in blob.ngrams(2) if len(time)>0 and ' '.join(i.lower()) in time]
        return self.replaceChuncks(TEXT, chuncks) 
        
    def day_time(self,TEXT):
        blob = TextBlob(TEXT, np_extractor=self.extractor)
        time = [(' '.join(i.lower())).encode('ascii','ignore') for i in blob.ngrams(2) if self.validate(' '.join(i))!=1]
        
        return time
        
    def checkCityName(self, Text):
        if self.cityname.CheckCityName(Text.capitalize()):
            return True
        return False
        
    def getCities(self,message):
        cities = []
        for items in message.split():
            if self.checkCityName(items):            
                cities.append(items)
        return cities
        
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
        
    def getSrc(self, TEXT, item):
        PLACES = self.getCities(TEXT)
        blob = TextBlob(TEXT, np_extractor=self.extractor)
        from_places = [(' '.join(i)) for i in blob.ngrams(2) if i[0]=='from' or i[0] == 'in' and i[i] in PLACES]
        if len(from_places)>0:
            SRC = from_places[0].split()[1].encode('ascii','ignore')
            for i in from_places:
                TEXT =  TEXT.replace(i.encode('ascii','ignore'), "")
        elif item=='Source':
            SRC = PLACES[0]
            TEXT =  TEXT.replace(SRC, "")
            
        else:
            SRC = ''
        return TEXT, SRC, PLACES
    
    def getDes(self, TEXT, PLACES, item):
        
        blob = TextBlob(TEXT, np_extractor=self.extractor)
        to_places = [(' '.join(i)) for i in blob.ngrams(2) if i[0]=='to' or i[0] == 'in' and i[i] in PLACES]
        if len(to_places)>0:        
            for i in to_places:
                TEXT =  TEXT.replace(i.encode('ascii','ignore'), "")
            DES = to_places[0].split()[1].encode('ascii','ignore')
        elif len(PLACES)==1 and item=='Destination':
            DES = PLACES[0]
            TEXT =  TEXT.replace(DES, "")
            
        else:
            DES = ''
        return TEXT, DES
        
    def getTime(self, TEXT):
        time = self.day_time(TEXT)
        if len(time)>0:
            TEXT = self.find_chunks(TEXT, time)
            TIME = ' '.join([i for i in TEXT.split() if '_' in i][0].encode('ascii','ignore').split('_'))
            TEXT = ' '.join([i for i in TEXT.split() if '_' not in i])
        else:
            TIME = ""
        return TEXT, TIME
        
    def text2int(self, textnum, numwords={}):
        if not numwords:
            units = ["zero", "one", "two", "three", "four", "five", "six", "seven", "eight",
                     "nine", "ten", "eleven", "twelve", "thirteen", "fourteen", "fifteen",
                     "sixteen", "seventeen", "eighteen", "nineteen",
                     ]
                
            tens = ["", "", "twenty", "thirty", "forty", "fifty", "sixty", "seventy", "eighty", "ninety"]
    
            scales = ["hundred", "thousand", "million", "billion", "trillion"]
    
            numwords["and"] = (1, 0)
            for idx, word in enumerate(units):    numwords[word] = (1, idx)
            for idx, word in enumerate(tens):     numwords[word] = (1, idx * 10)
            for idx, word in enumerate(scales):   numwords[word] = (10 ** (idx * 3 or 2), 0)
    
        current = result = 0
        for word in textnum.split():
            if word not in numwords:
              raise Exception("Illegal word: " + word)
    
            scale, increment = numwords[word]
            current = current * scale + increment
            if scale > 100:
                result += current
                current = 0
    
        return result + current
        
    def convertWordintoNumber(self, TEXT):
        units = ["zero", "one", "two", "three", "four", "five", "six", "seven", "eight",
                     "nine", "ten", "eleven", "twelve", "thirteen", "fourteen", "fifteen",
                     "sixteen", "seventeen", "eighteen", "nineteen","and"
                     ]
                
        tens = ["", "", "twenty", "thirty", "forty", "fifty", "sixty", "seventy", "eighty", "ninety"]
    
        scales = ["hundred", "thousand", "million", "billion", "trillion"]        
        l = []
        string_to_be_Replaced = []
        status =0 
        for i in TEXT.split():
            if i.lower() in units or i.lower() in tens or i.lower() in scales:
                l.append(i.lower())
                string_to_be_Replaced.append(i)
                status =1
        print ' '.join(string_to_be_Replaced), self.text2int(' '.join(l))       
        if status == 1:        
            TEXT = TEXT.replace(' '.join(string_to_be_Replaced), str(self.text2int(' '.join(l))))
        return TEXT
        
    def getAgenda(self, TEXT):
        
        TEXT = self.tokenize_only(self.remove_stopwords(TEXT.lower()))
        if TEXT != "":
            blob = TextBlob(TEXT, np_extractor=self.extractor)
            nps = blob.noun_phrases
            t=""
            
            #t has all NNs as capital so that NER works fine
            
            for x in TEXT.split():
                for i,j in blob.pos_tags:
                    if x==i:
                        if j=='NNP':
                            t = t + x.capitalize() + " "
                        else:
                            t = t+x+" "
                        break
            #nes = NamedEntitiesStanford()
            #loc,org,per = nes.GetEntities(t)
            s = MBSP.parse(t)
            intent_obj_list = [(i[4].split('-')[-1].encode('ascii','ignore'),i[0].encode('ascii','ignore')) for i in s.split()[0] if i[4]!='O' and 'SBJ' not in i[4].encode('ascii','ignore')]    
            
            probable_intent = [[elem for _, elem in group][0] for key, group in groupby(intent_obj_list, lambda pair: pair[0])]
            intent = []
            for i in probable_intent:
                c = 0
                for j in blob.noun_phrases:
                    if i in j:
                        c = 1
                if c==0:
                    intent.append(i)
            #prob_obj = [i[0].encode('ascii','ignore') for i in s.split()[0] if 'OBJ' in i[4].encode('ascii','ignore') or 'PRD' in i[4].encode('ascii','ignore')]
            probable_intent_obj = [[elem for _, elem in group] for key, group in groupby(intent_obj_list, lambda pair: pair[0])]
            intent_obj_clr_list = [i for i in probable_intent_obj for j in intent if j in i]
            intent_obj_clr = []            
            if len(intent_obj_clr_list)>0:
                intent_obj_clr = intent_obj_clr_list[0]
            intent_obj = [i for i in intent_obj_clr for j in s.split()[0] if i == j[0] and 'CLR' not in j[4]]
            obj = ' '.join(intent_obj[1:])
            if intent!= []:
                return obj, intent
            elif len(nps)>0:
                intent_obj = nps[0].encode('ascii','ignore').split()
                intent = intent_obj[0]
                obj = intent_obj[1]
                return obj, intent
            return '',''
        else:
            return '', ''
        
    def getOperator(self, NUMBER):
        if NUMBER == '':
            return ''
        else:
            return "Airtel"
        
    def getNumber(self, TEXT):
        s = MBSP.parse(TEXT).split()[0]
        number = [i[0] for i in s  if i[1]=='CD' and len(i[0])==10]
        count = 0
        msg = []
        if len(number)>0:
            for i in number:
                if not (i[0]=='9' or i[0]=='8' or i[0]=='7'):
                    TEXT = TEXT.replace(i, "")
                    if count ==0:
                        NUMBER = ""
                    msg.append(i+ "is invalid number")
                else:
                    if count ==0:
                        NUMBER = i.encode('ascii','ignore')  
                    else:
                        msg.append('multiple nos.')
                    TEXT = TEXT.replace(i, "")
                    count += 1
                
        else:
            NUMBER = ""
        return TEXT, NUMBER
                
    def getAmount(self, TEXT):
        TEXT = self.convertWordintoNumber(TEXT)
        if TEXT!= '':
            s = MBSP.parse(TEXT).split()[0]
            amount = [i[0] for i in s  if i[1]=='CD']
            if len(amount)>0:
                AMOUNT = amount[0].encode('ascii','ignore')  
                for i in amount:            
                    TEXT = TEXT.replace(i, '')
            else:
                AMOUNT = ""
            return TEXT, AMOUNT  
        else:
            return TEXT, ""
        
    def merge_dicts(self,*dict_args):
        '''
        Given any number of dicts, shallow copy and merge into a new dict,
        precedence goes to key value pairs in latter dicts.
        '''
        result = {}
        for dictionary in dict_args:
            result.update(dictionary)
        return result
        
    def getEntities(self,TEXT, category, item):
        if category == 'travel-and-tickets':
            TEXT, SRC, PLACES = self.getSrc(TEXT, item)
            #print TEXT
            TEXT, DES = self.getDes(TEXT, PLACES, item)
            #print TEXT
            TEXT, TIME = self.getTime(TEXT)
            #print TEXT
            obj, intent = self.getAgenda(TEXT)
            if type(intent)==list and intent!=[]:
                return {'SubCategory':obj,'INTENT':intent[0], 'Time and date': TIME, 'Source': SRC.encode('ascii','ignore'), 'Destination': DES.encode('ascii','ignore')}
            else:
                return {'SubCategory':obj,'INTENT':intent, 'Time and date': TIME, 'Source': SRC.encode('ascii','ignore'), 'Destination': DES.encode('ascii','ignore')}

        elif category == 'utility-and-bills':
            info = self.w.getEntities(TEXT, 'recharge')
            params = info[0]['params']
            intent = {}
            intent['INTENT'] = info[0]['action']
            info_dict = self.merge_dicts(params,intent)
            info_dict.update(intent)
            return info_dict
        elif category == 'beauty-services':
            obj, intent = self.getAgenda(TEXT)
            return {'SubCategory':obj,'INTENT':intent}

    def get_CategoryScore(self, message, category):
        prob_dist = self.cl.prob_classify(message)
        return prob_dist.prob(category)
        
    def getIntent(self, message, last_Category, item,last_score):
        category, score = tag_prob(message,self.cl)
        #print "Output of classifier:",category, score
        
        if last_score==0.0:
            Entities = self.getEntities(message, category, item)
            #print "Output of megamind:",category, str(score), Entities
            return category, score, Entities
        elif last_score > 0.5 and score < 0.8:
            Entities = self.getEntities(message, last_Category, item)
            #print "Output of megamind:", last_Category, str(self.get_CategoryScore(message, last_Category)), Entities
            return last_Category, last_score, Entities
        else:
            Entities = self.getEntities(message, category, item)
            #print "Output of megamind:",category, str(score), Entities
            return category, score, Entities
            
    def getStupidWitFormat(self, message, last_Category, item,last_score):
        category, score, Entities = self.getIntent(message, last_Category, item,last_score)
        return {'outcomes':[{'confidence':score,
                             'intent': category,
                             'entities': Entities
                             }
                            ]
                }
        
