# -*- coding: utf-8 -*-
"""
Created on Tue Feb 23 14:19:49 2016

@author: bibekbehera
"""

from pattern.en import parse, Sentence
from pattern.en import mood, modality

def create_list_of_transitions():
    file_to_read = '/Users/bibekbehera/Work/data/MT data/Training_sentences/tmp'
    with open(file_to_read) as f:
        content = f.readlines()
    list_of_transitions = []
    prev_list = []
    for sent in content:
        if "Chat ID" in sent:
            list_of_transitions.append(prev_list)
            prev_list=[]
            
        if "Customer :" in sent:    
            sent = (sent.split(":")[1]).split('\t')[0][1:]
            s = parse(sent, lemmata=True)
            s = Sentence(s)
            #print sent[0:len(sent)-1] + "\t" + mood(s) + "\t" + str(modality(s))
            prev_list.append(mood(s))
    
    list_of_transitions.append(prev_list)
    return list_of_transitions
        