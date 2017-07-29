# -*- coding: utf-8 -*-
"""
Created on Mon Apr 11 15:53:32 2016

@author: bibekbehera
"""
import numpy as np
from sklearn.cluster import KMeans 
from numbers import Number

#from nltk.corpus import stopwords
#import pandas as pd
from gensim.models import word2vec

#unlabeled_train = pd.read_csv('/Users/bibekbehera/Work/data/MT data/Training_sentences/chats_data_9thfeb.csv',header=0, delimiter="\t", quoting=3 )
#unlabeled_train_sent = [unlabeled_train.iget_value(i,0).split(',')[0] for i in range(0,105511)]
#stops = set(stopwords.words("english"))

#sentences = []
#for i in unlabeled_train_sent:
#    word_list = [j for j in i.split() if "_mt_cmmd" not in j and "00SPCLZZ" not in j]
#    sentences.append(word_list)
#
#num_features = 300    # Word vector dimensionality                      
#min_word_count = 40   # Minimum word count                        
#num_workers = 4       # Number of threads to run in parallel
#context = 10          # Context window size                                                                                    
#downsampling = 1e-3   # Downsample setting for frequent words
#
#print "Training model..."
#model = word2vec.Word2Vec(sentences, workers=num_workers, \
#            size=num_features, min_count = min_word_count, \
#            window = context, sample = downsampling)
#            
#model.init_sims(replace=True) #To optimize memory
#
#model_name = "300features_40minwords_10context"
#model.save(model_name)

model_name = "300features_40minwords_10context"
model = word2vec.Word2Vec.load(model_name)


word_Dict = []
vector_Dict = []
for key in model.vocab:
    word_Dict.append(key)
    vector_Dict.append(model[key])
df = np.array(vector_Dict)
labels_array = np.array(word_Dict)
clusters_to_make  = 40
kmeans_model = KMeans(init='k-means++', n_clusters=clusters_to_make, n_init=50)
kmeans_model.fit(df)
    
class autovivify_list(dict):
    '''Pickleable class to replicate the functionality of collections.defaultdict'''
    def __missing__(self, key):
            value = self[key] = []
            return value

    def __add__(self, x):
            '''Override addition for numeric types when self is empty'''
            if not self and isinstance(x, Number):
                    return x
            raise ValueError

    def __sub__(self, x):
            '''Also provide subtraction method'''
            if not self and isinstance(x, Number):
                    return -1 * x
            raise ValueError
                
def find_word_clusters(labels_array, cluster_labels):
    '''Read the labels array and clusters label and return the set of words in each cluster'''
    cluster_to_words = autovivify_list()
    for c, i in enumerate(cluster_labels):
            cluster_to_words[i].append(labels_array[c])
    return cluster_to_words
        
cluster_labels    = kmeans_model.labels_
cluster_inertia   = kmeans_model.inertia_
cluster_to_words  = find_word_clusters(labels_array, cluster_labels)

for i in cluster_to_words:
    if 'menu' in cluster_to_words[i]:
        print cluster_to_words[i]