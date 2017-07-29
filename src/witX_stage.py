# -*- coding: utf-8 -*-
"""
Created on Wed Mar 23 21:02:50 2016

@author: bibekbehera
"""


from textblob import TextBlob, Word
from textblob.np_extractors import ConllExtractor
from nltk.corpus import stopwords
import nltk,re, os
from UserName import UserName
from itertools import groupby
import Levenshtein as le
import subprocess

abs_path = os.path.dirname(os.path.abspath('__file__'))

class witX():
    
    def __init__(self):
        self.extractor = ConllExtractor()
        self.stopwords = nltk.corpus.stopwords.words('english')
        
        
    def getMBSPParse(self,text):
        cmd = 'curl -X POST --include \'https://textanalysis.p.mashape.com/mbsp-parse\' -H \'X-Mashape-Key: Sl5LB6XcMkmshpmqAjGref1moOc1p1vUk2GjsnPxZLZLm7g7Jq\' -H \'ContentType: application/x-www-form-urlencoded\' -H \'Accept: application/json\' -d \'text='+text+'\''
        x = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE).stdout.read()
        index = x.index("result")
        return x[index:-1].split(':')[1].split('\n')[0][2:-1].decode('utf-8','ignore')
        
    def remove_stopwords(self,sent):
        l = []   
        
        for i in sent.split():
            stopword_filtered = [j for j in self.stopwords if len(i)==len(j)]
            status, item = self.levenshteinComparison(i,stopword_filtered)
            if not status:
                l.append(i)
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
        #print ' '.join(string_to_be_Replaced), self.text2int(' '.join(l))       
        if status == 1:        
            TEXT = TEXT.replace(' '.join(string_to_be_Replaced), str(self.text2int(' '.join(l))))
        return TEXT
        
    def getName(self,TEXT):
        u = UserName()
        TEXT = TEXT.replace("'s",'')
        for i in TEXT.split():
            if u.CheckPersonName(i):
                NAME = i
                TEXT = TEXT.replace(i,"")
                return TEXT, NAME
        return TEXT, ''
        
    def getStringsSeparatedByConjunction(self,TEXT):
        s = self.getMBSPParse(TEXT)
        list_of_strings = []
        string = ""
        MBSP_array = [i.split('/') for i in s.split()]
        for i in MBSP_array :
            if i[1]=='CC' or i[0] == 'also':
                list_of_strings.append(string.encode('ascii','ignore'))                
                string = ""
            else:
                string = string + i[0] + " "
        list_of_strings.append(string.encode('ascii','ignore')) 
        return list_of_strings
                
                
    def getAgenda(self, TEXT):
        
        TEXT = self.tokenize_only(self.remove_stopwords(TEXT.lower()))
        if TEXT != "":
            blob = TextBlob(TEXT, np_extractor=self.extractor)
            nps = blob.noun_phrases
            t = TEXT            
            s = self.getMBSPParse(t)
            MBSP_array = [i.split('/') for i in s.split()]
            intent_obj_list = [(i[4].split('-')[-1].encode('ascii','ignore'),i[0].encode('ascii','ignore')) for i in MBSP_array  if i[4]!='O' and 'SBJ' not in i[4].encode('ascii','ignore')]    
            probable_intent = [[elem for _, elem in group][0] for key, group in groupby(intent_obj_list, lambda pair: pair[0])]
            intent = []
            for i in probable_intent:
                c = 0
                for j in blob.noun_phrases:
                    if i in j:
                        c = 1
                if c==0:
                    intent.append(i)
            #prob_obj = [i[0].encode('ascii','ignore') for i in MBSP_array  if 'OBJ' in i[4].encode('ascii','ignore') or 'PRD' in i[4].encode('ascii','ignore')]
            probable_intent_obj = [[elem for _, elem in group] for key, group in groupby(intent_obj_list, lambda pair: pair[0])]
            intent_obj_clr_list = [i for i in probable_intent_obj for j in intent if j in i]
            intent_obj_clr = []            
            if len(intent_obj_clr_list)>0:
                intent_obj_clr = intent_obj_clr_list[0]
            intent_obj = [i for i in intent_obj_clr for j in MBSP_array  if i == j[0] and 'CLR' not in j[4]]
            obj = ' '.join(intent_obj[1:])
            if intent!= []:
                return obj, intent[0]
            elif len(nps)>0:
                intent_obj = nps[0].encode('ascii','ignore').split()
                intent = intent_obj[0]
                obj = intent_obj[1]
                return obj, intent
            return '', TEXT
        else:
            return '', ''
        
    def getAgendaV2(self, TEXT):
        
        TEXT = TEXT.capitalize()
        if TEXT != "":
            blob = TextBlob(TEXT, np_extractor=self.extractor)
            nps = blob.noun_phrases
            t = TEXT            
            s = self.getMBSPParse(t)
            MBSP_array = [i.split('/') for i in s.split()]
            subj_list = [i[0].encode('ascii','ignore') for i in MBSP_array  if i[4]!='O' and 'SBJ' in i[4].encode('ascii','ignore')]
            subj = ' '.join(subj_list)
            #print subj
            intent_obj_list = [(i[4].split('-')[-1].encode('ascii','ignore'),i[0].encode('ascii','ignore')) for i in MBSP_array  if i[4]!='O' and 'SBJ' not in i[4].encode('ascii','ignore')]    
            probable_intent = [[elem for _, elem in group][0] for key, group in groupby(intent_obj_list, lambda pair: pair[0])]
            intent = []
            for i in probable_intent:
                c = 0
                for j in blob.noun_phrases:
                    if i in j:
                        c = 1
                if c==0:
                    intent.append(i)
            #prob_obj = [i[0].encode('ascii','ignore') for i in MBSP_array  if 'OBJ' in i[4].encode('ascii','ignore') or 'PRD' in i[4].encode('ascii','ignore')]
            probable_intent_obj = [[elem for _, elem in group] for key, group in groupby(intent_obj_list, lambda pair: pair[0])]
            intent_obj_clr_list = [i for i in probable_intent_obj for j in intent if j in i]
            intent_obj_clr = []            
            if len(intent_obj_clr_list)>0:
                intent_obj_clr = intent_obj_clr_list[0]
            intent_obj = [i for i in intent_obj_clr for j in MBSP_array if i == j[0] and 'CLR' not in j[4]]
            obj = ' '.join(intent_obj[1:])
            if intent!= []:
                #print subj, obj
                return subj, self.remove_stopwords(obj), intent[0]
            elif len(nps)>0:
                intent_obj = nps[0].encode('ascii','ignore').split()
                intent = intent_obj[0]
                obj = intent_obj[1]
                #print subj
                return subj, self.remove_stopwords(obj), intent
            
            return subj,'', TEXT
        else:
            return '','', ''
    def getOperatorfromNumber(self, NUMBER):
        if NUMBER == '':
            return ''
        else:
            return "Airtel"
    
    def getLevenshteinEquivalentWord(self,word1,word2,threshold):
        if isinstance(word1, unicode) and isinstance(word2, unicode):
            if le.distance(word1.encode('ascii','ignore'), word2.encode('ascii','ignore')) <= threshold:
                return True, word2.encode('ascii','ignore')
        if isinstance(word1, unicode) and not isinstance(word2, unicode):
            if le.distance(word1.encode('ascii','ignore'), word2) <= threshold:
                return True, word2
        if not isinstance(word1, unicode) and isinstance(word2, unicode):
            if le.distance(word1, word2.encode('ascii','ignore')) <= threshold:
                return True, word2.encode('ascii','ignore')
        if not isinstance(word1, unicode) and not isinstance(word2, unicode):
            if le.distance(word1, word2) <= threshold:
                return True, word2
        return False, ''
    
    def levenshteinComparison(self, word, list_of_words):
        if len(word)>2:
            for i in list_of_words:
                status, word2 = self.getLevenshteinEquivalentWord(word,i,1)
                if status:
                    return True, i
        else:
            for i in list_of_words:
                status, word2 = self.getLevenshteinEquivalentWord(word,i,0)
                if status:
                    return True, i
        return False, ''
        
    def getOperatorFromText(self, TEXT, list_of_operators):
        operator = ''        
        for i in TEXT.split():
            flag, oper = self.levenshteinComparison(i.lower(),list_of_operators)
            if flag:
                TEXT = TEXT.replace(i,"")
                operator = oper
        if operator == '':
            operator = 'no operator'
        return TEXT, operator
        
    def getBillTypeFromText(self, TEXT):
        list_of_bill_types = {'electricity':['electricity','bijli','current'], 'DTH':['dth'], 'landline':['landline','telephone'], 'insurance':['insurance','bima']}   
        list_of_operators = {'DTH':['Dish TV','Tata Sky','Reliance Big TV','Videocon D2H','Sun Direct','Airtel DTH'],
                             'electricity':['Reliance Energy Mumbai','BSES Rajdhani','BSES Yamuna','MSEB Mumbai', 'Tata Power Delhi Distribution Ltd','BEST', 'Chhattisgarh Electricity Board', 'Noida Power Company Limited', 'Jaipur Vidyut Vitran Nigam Ltd', 'Bangalore Electricity Supply BESCOM','MP Paschim Vidyut Vitaran INDORE', 'Jamshedpur Utilities & Services JUSCO'],
                             'landline': ['Airtel Landline','MTNL Delhi', 'Tata TeleServices', 'Reliance Communications', 'Tikona'],
                             'insurance':['ICICI','TATA','Birla']                             
                             
                             }
        bill_type = ''        
        for i in TEXT.split():
            for j in list_of_bill_types.keys():
                flag, bill = self.levenshteinComparison(i.lower(),list_of_bill_types[j])
                if flag:
                    TEXT = TEXT.replace(i,"")
                    bill_type = j
        if bill_type:        
            TEXT, OPERATOR = self.getOperatorFromText(TEXT, list_of_operators[bill_type])
        else: #fallback when type is not mentioned in message like BSES YAmuna or 50 rs
            for i in TEXT.split():
                for j in list_of_operators.keys():
                    flag, bill = self.levenshteinComparison(i.lower(), list_of_operators[j])
                    if flag:
                        bill_type = j
                        TEXT = TEXT.replace(j,"")
                        break
                    
            if bill_type:
                TEXT, OPERATOR = self.getOperatorFromText(TEXT, list_of_operators[bill_type])
            else:            
                OPERATOR = ''
        return TEXT, bill_type, OPERATOR
        
    def validate_number(self,TEXT):
        if (TEXT[0]=='9' or TEXT[0]=='8' or TEXT[0]=='7') and len(TEXT)==10:
            return True
        else:
            return False
            
    def getNumber(self, TEXT):
        s = self.getMBSPParse(TEXT)
        MBSP_array = [i.split('/') for i in s.split()]
        number = [i[0] for i in MBSP_array  if i[1]=='CD' and len(i[0])==10]
        NUMBER = ''
        count = 0
        msg = []
        if len(number)>0:
            for i in number:
                if not self.validate_number(i):
                    TEXT = TEXT.replace(i, "")
                    if count ==0:
                        NUMBER = ''
                    msg.append(i+ " is invalid number")
                else:
                    if count ==0:
                        NUMBER = i.encode('ascii','ignore')  
                    else:
                        msg.append('multiple nos.')
                    TEXT = TEXT.replace(i, '')
                    count += 1
            #print msg
                
        else:
            for s in TEXT.split():
                number_list = re.findall("[-+]?\d+[\.]?\d*", s)
                if number_list!=[]:
                    number = number_list[0]
                    #print number
                    if self.validate_number(number):
                        NUMBER = number
                        TEXT = TEXT.replace(s, '')
        return TEXT.encode('ascii','ignore'), NUMBER, msg
                
    def getAmount(self, TEXT):
        if TEXT!= '':
            TEXT = self.convertWordintoNumber(TEXT)
        
            s = self.getMBSPParse(TEXT)
            MBSP_array = [i.split('/') for i in s.split()]
            amount = [i[0] for i in MBSP_array  if i[1]=='CD' and len(i[0])<=4]
            if len(amount)>0:
                AMOUNT = amount[0].encode('ascii','ignore')  
                for i in amount:            
                    TEXT = TEXT.replace(i, '')
            else:
                AMOUNT = ""
            return TEXT, AMOUNT  
        else:
            return TEXT, ""
        
    def findNumber(self, TEXT, lower_limit, upper_limit):
        NUMBER = ''
        for s in TEXT.split():
            number_list = re.findall("[-+]?\d+[\.]?\d*", s)
            if number_list!=[]:
                number = [i for i in number_list if len(i)>=lower_limit and len(i)<=upper_limit]
                #print number
                if number:
                    NUMBER = number[0]
                    TEXT = TEXT.replace(NUMBER, '')
        return TEXT, NUMBER
        
    def getCustomerNumber(self, TEXT, bill_type):
        if bill_type == 'landline':
            lower_limit = 11
            upper_limit = 13
                
        elif bill_type == 'electricity':
            lower_limit = 9
            upper_limit = 10
            
        elif bill_type == 'insurance':
            lower_limit = 10
            upper_limit = 8
            
        elif bill_type == 'DTH':
            lower_limit = 11
            upper_limit = 11
            
        else:
            TEXT, NUMBER = self.findNumber(TEXT, 11, 11)
            if not NUMBER:
                TEXT, NUMBER = self.findNumber(TEXT, 11, 13)
                if not NUMBER:
                    TEXT, NUMBER = self.findNumber(TEXT, 8, 8)
                    if not NUMBER:
                        TEXT, NUMBER = self.findNumber(TEXT, 9, 10)
                        if NUMBER:
                            return TEXT, NUMBER, 'electricity'
                        else:
                            return TEXT, NUMBER, ''
                    return TEXT, NUMBER, 'insurance'
                return TEXT, NUMBER, 'landline'
            return TEXT, NUMBER, 'DTH'
        TEXT, NUMBER = self.findNumber(TEXT, lower_limit, upper_limit)
        return TEXT, NUMBER, bill_type
            
    def findRelative(self, TEXT, relative):
        for i in relative:
            if i in TEXT:
                return i, True
        return '', False
        
    def getRelatives(self, TEXT):
        relative = ['mom', 'dad', 'sis', 'bro']
        for i in TEXT.split():
            rel, status = self.findRelative(i,relative)
            if status:
                TEXT = TEXT.replace(i,'')
                return TEXT,rel
        return TEXT, ''
    
    def mapIntent(self, TEXT, operator):
        if operator:
            return 'change_operator'
        Intent = {'support':['support', 'contact support'], 'cancel':['cancel order', 'cancel', 'revoke order', 'revoke'], 'order_status':['show order', 'show status', 'send order status'],'show_plans':['show plans'],'change_operator':['change operator', 'operator','shift'],'recharge':['recharge','put','charge']}
        for i in Intent.keys():
            list_of_words = Intent[i]
            _,status = self.levenshteinComparison(TEXT,list_of_words)
            if status:
                return i
        return 'recharge'
                
    
    def getEntityForRecharge(self,TEXT):
        TEXT, NUMBER, msg = self.getNumber(TEXT)
            
        TEXT, AMOUNT = self.getAmount(TEXT)
        TEXT, NAME = self.getName(TEXT)
        TEXT, PLAN = self.getPlanType(TEXT)
        TEXT, RECHARGE = self.getRechargeType(TEXT)
        list_of_operators = ['airtel', 'vodafone', 'idea', 'reliance', 'aircel', 'docomo', 'bsnl', 'mtnl', 'videocon', 'mts']        
        TEXT, likely_operator = self.getOperatorFromText(TEXT, list_of_operators)
        if likely_operator != 'no operator':
            OPERATOR = likely_operator
        else:
            OPERATOR = ''
            
        if not NAME:
            TEXT, NAME = self.getRelatives(TEXT)
        SUBCATEGORY, INTENT = self.getAgenda(TEXT)
        #print INTENT,SUBCATEGORY
        if INTENT and SUBCATEGORY:
            FINAL_INTENT = self.mapIntent(INTENT+" "+SUBCATEGORY, OPERATOR)
        elif not INTENT and SUBCATEGORY:
            FINAL_INTENT = self.mapIntent(SUBCATEGORY, OPERATOR)
        elif INTENT and not SUBCATEGORY:
            FINAL_INTENT = self.mapIntent(INTENT, OPERATOR)
        else:
            FINAL_INTENT = self.mapIntent('', OPERATOR)
        return {'params':{'OPERATOR':OPERATOR, 'NUMBER':NUMBER, 'AMOUNT':AMOUNT, 'NAME': NAME,'PLAN_TYPE':PLAN,'RECHARGE_TYPE':RECHARGE},'action': FINAL_INTENT, 'score':1.0}
        
    def getEntityForUtility(self,TEXT):
        TEXT, BILL_TYPE, OPERATOR = self.getBillTypeFromText(TEXT)
        
        TEXT, CN, BILL_TYPE = self.getCustomerNumber(TEXT, BILL_TYPE)
        TEXT, AMOUNT = self.getAmount(TEXT)
        return {'params':{'operator':OPERATOR, 'consumer_number':CN,'amount':AMOUNT},'action': BILL_TYPE, 'score':1.0}
    
#    def getEntityForEcommerce(self,TEXT):
#        TEXT, SUBC = self.getCategoryType(TEXT)
#        return {'params':{'Category':SUBC},'action':}        
    def getEntityForEachIntent(self,TEXT,topic):
        TEXT = ' '.join(TEXT.split())
        if topic=='recharge':
            return self.getEntityForRecharge(TEXT)
        if topic=='utility':
            return self.getEntityForUtility(TEXT)
        if topic=='ecommerce':
            return self.getEntityForEcommerce(TEXT)
        
    def checkSpelling(self, TEXT):
        s = []        
        for i in TEXT.split():
            w = Word(i)
            correct_word = w.spellcheck()[0][0]
            s.append(correct_word)
            
        return ' '.join(s)
            
    def EntityIdentifier(self, TEXT, list_entity):
        for i in TEXT.split():
            status, word = self.levenshteinComparison(i, list_entity)
            if status:
                TEXT = TEXT.replace(i,'')
                return TEXT,word
        return TEXT,''
        
    def getRechargeType(self, TEXT):
        recharge_type = ['postpaid','prepaid']        
        return self.EntityIdentifier(TEXT, recharge_type)
    
    def getPlanType(self, TEXT):
        plan_type= ['data', 'topup', 'validity', 'sms','special']
        return self.EntityIdentifier(TEXT, plan_type)
    
    def getOrderList(self, multiple_agenda, latest_intent, topic):
        index_last_item = len(multiple_agenda)
        if topic == 'recharge':
            for i in multiple_agenda[index_last_item-1]['params'].keys():
                if not multiple_agenda[index_last_item-1]['params'][i]:                
                    multiple_agenda[index_last_item-1]['params'][i] = latest_intent['params'][i]
        if topic == 'utility':
            for i in multiple_agenda[index_last_item-1]['params'].keys():
                if not multiple_agenda[index_last_item-1]['params'][i]:                
                    multiple_agenda[index_last_item-1]['params'][i] = latest_intent['params'][i]
        if not multiple_agenda[index_last_item-1]['action']:
                    multiple_agenda[index_last_item-1]['action'] = latest_intent['action']
        return multiple_agenda
                    
        
            
    def getMultipleIntent(self, TEXT, topic):
        list_of_strings = self.getStringsSeparatedByConjunction(TEXT)
        multiple_agenda = []
        for i in list_of_strings:
            
            latest_intent = self.getEntityForEachIntent(i, topic)
            index_last_item = len(multiple_agenda)
            #print latest_intent
            if index_last_item==0:
                multiple_agenda.append(latest_intent)
                
            elif latest_intent['action']!= multiple_agenda[index_last_item-1]['action'] and latest_intent['action']!='':
                multiple_agenda.append(latest_intent)
            
            elif topic == 'recharge':
                if latest_intent['params']['NAME'] != multiple_agenda[index_last_item-1]['params']['NAME']:
                    multiple_agenda.append(latest_intent)
                if latest_intent['params']['NUMBER'] != multiple_agenda[index_last_item-1]['params']['NUMBER']:
                    multiple_agenda.append(latest_intent)
            else:
                
                
                multiple_agenda = self.getOrderList(multiple_agenda, latest_intent, topic)
                
                
            #print multiple_agenda
                
                    
                
            #print self.getAgenda(i)
        return multiple_agenda
        
    def getSentenceCombiner(self, TEXT):
        list_of_punctuation = ['.',':','!']
        if TEXT[len(TEXT)-1] in list_of_punctuation:
            TEXT = TEXT[:-1]
        TEXT = TEXT.replace('.',' and ')
        TEXT = TEXT.replace(':',' and ')
        TEXT = TEXT.replace('!',' and ')
        return TEXT
    
    def getEntities(self,TEXT, category):
        TEXT = self.getSentenceCombiner(TEXT)
        intent = self.getMultipleIntent(TEXT,category)
        #print TEXT
            
        if type(intent)==list and intent!=[]:
            return intent
        else:
            return intent
        

    def getStupidWitFormat(self, message, last_Category, item,last_score):
        category, score, Entities = self.getIntent(message, last_Category, item,last_score)
        return {'outcomes':[{'confidence':score,
                             'intent': category,
                             'entities': Entities
                             }
                            ]
                }
                
class main():
    def test(self,msg,category):
        w = witX()
        return w.getEntities(msg,category)

m = main()
m.test('recharge my moms phone for 50 rs','recharge')