# -*- coding: utf-8 -*-
"""
Created on Mon Apr 25 12:11:32 2016

@author: bibekbehera
"""
import MBSP,rake
def subject_object_pair(text):
    s = MBSP.parse(text)
    intent_obj_list = []
    no_of_pairs = max([i[4].split('-')[-1] for i in s.split()[0] if i[4].split('-')[-1]!=u'O'])
    for j in range(1,int(no_of_pairs)+1):
        intent_obj_list.append(' '.join([i[0].encode('ascii','ignore') for i in s.split()[0] if str(j) in i[4].split('*')[0]]))
    pp_pairs = list(set([i[5].split('-')[-1] for i in s.split()[0] if i[5].split('-')[-1]!=u'O' and u'P' in i[5].split('-')[-1]]))
    prepositional_pairs = []  
    for j in pp_pairs:
        prepositional_pairs.append((' '.join([i[0].encode('ascii','ignore') for i in s.split()[0] if j in i[5]])))
    return intent_obj_list + prepositional_pairs
    
def keyword_extraction(phrase_list):
    stoppath = '/Users/bibekbehera/nltk_data_new/nltk_data/corpora/stopwords/english'
    rake_object = rake.Rake(stoppath)
    keywords = [j[0] for text in phrase_list for j in rake_object.run(text)]
    return keywords
        