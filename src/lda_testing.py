# -*- coding: utf-8 -*-
"""
Created on Mon Jan 25 16:01:18 2016

@author: bibekbehera
"""
from gensim import models, utils
import cPickle
#load while testing
topics = ['beauty-services',
          'beauty-services',#'meat',
          'travel-and-tickets',#'laundry',
          'utility-and-bills',
          'beauty-services',#'travel-and-tickets',
          'beauty-services',#'dispute_resolution_address',
          'beauty-services',#'goal-fulfilment',
          'beauty-services'#'home-services',
          #'beauty-services',#'customary',
          #'beauty-services'#'Utility'
          ]
with open('/Users/bibekbehera/Work/analytics_nlp/analytics_nlp/Jarvis2/src/corpus','rb') as fid:
    corpus = cPickle.load(fid)
model = models.wrappers.LdaMallet.load('model')

def get_topic(msg):
    doc = msg
    bow = corpus.dictionary.doc2bow(utils.simple_preprocess(doc))
    l = [b for (a,b) in model[bow]]
    index = [i for i in range(0,len(l)) if l[i] == max(l)][0]
    #print model.print_topic(index)
    return (topics[index], max(l))
