# -*- coding: utf-8 -*-
"""
Created on Tue Jan 19 16:46:49 2016

@author: bibekbehera
"""

import logging, cPickle
import os
from gensim import corpora, models, utils
logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

 
def iter_documents(reuters_dir):
    """Iterate over Reuters documents, yielding one document at a time."""
    for fname in os.listdir(reuters_dir):
        # read each document as one big string
        document = open(os.path.join(reuters_dir, fname)).read()
        # parse document into a list of utf8 tokens
        yield utils.simple_preprocess(document)
 
class ReutersCorpus(object):
    def __init__(self, reuters_dir):
        self.reuters_dir = reuters_dir
        self.dictionary = corpora.Dictionary(iter_documents(reuters_dir))
        self.dictionary.filter_extremes()  # remove stopwords etc
 
    def __iter__(self):
        for tokens in iter_documents(self.reuters_dir):
            yield self.dictionary.doc2bow(tokens)
 
# set up the streamed corpus
corpus = ReutersCorpus('/Users/bibekbehera/Work/data/MT data/Training_sentences/chatfolder')
with open('corpus','wb') as fid:
    cPickle.dump(corpus,fid)
    
#with open('corpus','rb') as fid:
#    corpus = cPickle.load(fid)
    
# INFO : adding document #0 to Dictionary(0 unique tokens: [])
# INFO : built Dictionary(24622 unique tokens: ['mdbl', 'fawc', 'degussa', 'woods', 'hanging']...) from 7769 documents (total 938238 corpus positions)
# INFO : keeping 7203 tokens which were in no less than 5 and no more than 3884 (=50.0%) documents
# INFO : resulting dictionary: Dictionary(7203 unique tokens: ['yellow', 'four', 'resisted', 'cyprus', 'increase']...)
 
# train 10 LDA topics using MALLET
mallet_path = '/Users/bibekbehera/Downloads/mallet-2.0.7/bin/mallet'
model = models.wrappers.LdaMallet(mallet_path, corpus, num_topics=8, id2word=corpus.dictionary)

with open('model','wb') as fid:
    cPickle.dump(model,fid)


# ...
#0	5	id slot book laundry wash service tomorrow iron rate flat time discount job email ahead dry pm gmail give 
#1	5	payment bill pay amount send link number discount make kindly give rs recharge id account electricity moment due paid 
#2	5	check give time moment call today revert details store ll vendor information assist inconvenience price play plz send don 
#3	5	rs full facial wax discount normal pedicure hair beauty spa lotus waxing manicure services slot half book detan hands 
#4	5	bangalore give assist check hyderabad moment address information road location kindly nagar contact revert details main floor st provide 
#5	5	order delivery runner delivered minutes address rs confirm deliver noted place details price kg confirmed cost vendor give kindly 
#6	5	services service beauty provide inform hyderabad home massage city card app offers ur list assist booking food kind offer 
#7	5	kindly pm tickets give movie moment book ticket email check date time today preferred id details assist bangalore noted 
#8	5	back city request response awaiting leave today offline tiger magic assist full good morning ping email free open day 
#9	5	order delivery online food place time restaurant biryani rs give chicken charges min cost deliver moment address confirm veg 
# 
# <1000> LL/token: -7.5002
# 
# Total time: 34 seconds
 

