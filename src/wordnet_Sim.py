# -*- coding: utf-8 -*-
"""
Created on Tue Feb 23 19:24:16 2016

@author: bibekbehera
"""

from nltk.corpus import wordnet as wn
from nltk.corpus import wordnet_ic
from pattern.en import wordnet as wnp
import MBSP, nltk
brown_ic = wordnet_ic.ic('ic-brown.dat')

class preprocessing():
    def __init__(self):
        self.stopwords = nltk.corpus.stopwords.words('english')
    
    def get_synonym(self,word,pos1,pos2):
        for i in wn.synsets(word, pos1):
            for j in i.lemma_names():
                if self.get_antonym(j, pos2) !=  "antonym not available":
                    return j
        #synonym_synset = wn.synsets(synonym, pos)[0]
        #return synonym#recall.res_similarity(synonym_synset, brown_ic)
        
    def get_antonym(self,word, pos):
        word_synset = wnp.synsets(word, pos)[0]
        try:
            antonym = word_synset.antonym.synonyms[0]
        except:
            return "antonym not available"
        return antonym
        
    def replaceChuncks(self,TEXT, chuncks, pos1, pos2):
            for item in chuncks:
                if item.replace('_',' ') in TEXT:
                    index = TEXT.index(item.replace('_',' '))
                    if TEXT[index-1]==' ':
                        TEXT = TEXT.replace(item.replace('_',' '),self.get_antonym(self.get_synonym(item.split('_')[-1], pos1,pos2), pos2))
                    else:
                        replacement = ' '+self.get_antonym(self.get_synonym(item.split('_')[-1], pos1,pos2), pos2)
                        TEXT = TEXT.replace(item.replace('_',' '), replacement)
            return TEXT
        
    def find_chunks(self,TEXT, t):
        chuncks = ['_'.join([t[i][0],t[i+1][0]]) for i in range(0,len(t)) if (t[i][1] == 'RB' or t[i][1] == 'VBP') and i != len(t)-1 and t[i+1][1] =='VB']
        #print chuncks
        return self.replaceChuncks(TEXT, chuncks, 'v', "VB") 
        
    def remove_stopwords(self,sent):
            l = [i for i in sent.split() if i not in self.stopwords]
            return ' '.join(l)
        
    def remove_negations(self,s):
        t = MBSP.parse(s).split()[0]
        negation_free_string =  self.find_chunks(s,t)
        intent = self.remove_stopwords(negation_free_string.lower())
        return intent
    
    

