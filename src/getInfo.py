# -*- coding: utf-8 -*-
"""
Created on Tue Nov 10 10:58:10 2015

@author: bibekbehera
"""

from textblob import TextBlob
from textblob.np_extractors import ConllExtractor
from nltk.corpus import stopwords
from dateutil import parser
import MBSP, nltk,re
from itertools import groupby

def validate(time_text):
        try:
            parser.parse(time_text)
        except ValueError:
            return 1

def remove_stopwords(sent):
    stopwords = nltk.corpus.stopwords.words('english')
    l = [i for i in sent.split() if i not in stopwords]
    return ' '.join(l)

def tokenize_only(text):
    # first tokenize by sentence, then by word to ensure that punctuation is caught as it's own token
    tokens = [word.lower() for sent in nltk.sent_tokenize(text) for word in nltk.word_tokenize(sent)]
    filtered_tokens = []
    # filter out any tokens not containing letters (e.g., numeric tokens, raw punctuation)
    for token in tokens:
        if re.search('[a-zA-Z]', token):
            filtered_tokens.append(token)
    return ' '.join(filtered_tokens)
    
def GetSubCategory(TEXT):
#    with open('/Users/bibekbehera/my_dumped_classifier_afterStemming.pkl', 'rb') as fid:
#        cl = cPickle.load(fid)
#    category, score = tag_prob(TEXT,cl)
    TEXT = tokenize_only(remove_stopwords(TEXT.lower()))
    extractor = ConllExtractor()
    blob = TextBlob(TEXT, np_extractor=extractor)
    nps = blob.noun_phrases
    t=""
    
    #t has all NNs as capital so that NER works fine
    time = [(' '.join(i)).encode('ascii','ignore') for i in blob.ngrams(3) if validate(' '.join(i))!=1]
    if len(time)==0:
        time = [(' '.join(i)).encode('ascii','ignore') for i in blob.ngrams(2) if validate(' '.join(i))!=1]
    
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
    if intent_obj_list!=[]:    
        probable_intent = [[elem for _, elem in group][0] for key, group in groupby(intent_obj_list, lambda pair: pair[0])]
        intent = []
        for i in probable_intent:
            c = 0
            for j in blob.noun_phrases:
                if i in j:
                    c = 1
            if c==0:
                intent.append(i)
        prob_obj = [i[0].encode('ascii','ignore') for i in s.split()[0] if 'OBJ' in i[4].encode('ascii','ignore') or 'PRD' in i[4].encode('ascii','ignore')]
        probable_intent_obj = [[elem for _, elem in group] for key, group in groupby(intent_obj_list, lambda pair: pair[0])]
        intent_obj_clr_list = [i for i in probable_intent_obj for j in intent if j in i]
        if len(intent_obj_clr_list)>0:
            intent_obj_clr = intent_obj_clr_list[0]
        intent_obj = [i for i in intent_obj_clr for j in s.split()[0] if i == j[0] and 'CLR' not in j[4]]
        obj = ' '.join(intent_obj[1:])
    else:
        intent =''
        obj = t
        
#    probable_list_of_entities = list(set([i.encode('ascii','ignore') for i in nps])|set([a for a,b in getKeywords(TEXT)]))    
#    if len(time)==0:
#        probable_list_of_places = [a for a in probable_list_of_entities if obj.lower() not in a and a!=sbj.lower()]
#    else:
#        probable_list_of_places = [a for a in probable_list_of_entities for t1 in time if obj.lower() not in a and a!=sbj.lower() and (t1.lower() not in a and a not in t1.lower())]
#    list_of_places_from_MBSP_and_blob = [(i,j) for i in probable_list_of_places for j in loc if j.lower() in i]
#    list_of_places = [' '.join([elem for _, elem in group]) for key, group in groupby(list_of_places_from_MBSP_and_blob, lambda pair: pair[0])]
#    from_places = [(' '.join(i[1:])) for i in blob.ngrams(2) if i[0]=='from' or i[0] == 'in']
#    FROM_PLACES = [j for i in from_places for j in probable_list_of_places if i.lower() in j.lower()]
#    if len(FROM_PLACES) > 0:
#        NPs_place_to = [x.encode('ascii','ignore') for x in probable_list_of_places for y in FROM_PLACES if x!=y.lower()]
#    else:
#        NPs_place_to = [x.encode('ascii','ignore') for x in probable_list_of_places]

#    to_places = [(' '.join(i[1:])) for i in blob.ngrams(2) if i[0]=='to' or i[0]=='at']
#    TO_PLACES = [j for i in to_places for j in NPs_place_to if i.lower() in j.lower()]
    #DAY_TOMORROW = 1 if 'tomorrow' in text
    #return {'PERSON': sbj, 'INTENT':intent, 'CATEGORY':(category,score,{'SUBCATEGORY':obj}), 'PLACES':{'SRC':FROM_PLACES,'DST':TO_PLACES}, 'TIME':time}
#    return {u'customer': sbj, u'destination': TO_PLACES,u'source': FROM_PLACES,u'subCategory':obj,u'INTENT':intent, u'TIME':time}
    if type(intent)==list:
        return obj,intent[0] 
    else:
        return obj,intent