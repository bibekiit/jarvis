# -*- coding: utf-8 -*-
"""
Created on Fri Mar 25 12:53:12 2016

@author: bibekbehera
"""

import feedparser
import mechanize
from bs4 import BeautifulSoup

import time, re
from collections import defaultdict
import math, operator
from nltk.tokenize import sent_tokenize,word_tokenize
from heapq import nlargest
from nltk.corpus import stopwords
from math import log
from numpy import asarray, sum, zeros
from scipy.linalg import svd
import urllib2
stopwords = stopwords.words('english') 
stopwords = [x.encode('utf-8') for x in stopwords]
punctuations = '''()?".,:'!''' 

class retriever:
    
    def __init__(self):
        self.feed_name = ['FP','DH','CNN']
        self.url = ['http://www.thehindu.com/sport/?service=rss',
                    'http://feeds.hindustantimes.com/HT-Cricket-TopStories',
                    'http://timesofindia.indiatimes.com/rssfeeds/4719161.cms']
        self.feed_links = {'FP':[],'DH':[],'CNN':[]}
        self.max_links = 5
               
                    
    def Retriever2Aggregator(self,dbc):
        # This function is called by aggregator which gives it right to read from db
        for i in range(0,len(self.feed_name)):
            feed = feedparser.parse(self.url[i])
    
        #
        # figure out which posts to print
        #
            posts_to_print = []
            posts_to_skip = []
        
            for post in feed.entries:
                # if post is already in the database, skip it
                # TODO check the time
                if "thehindu" in self.url[i] or "hindustantimes" in self.url[i]:
                    link = post.link
                else:
                    link = post.id
                if dbc.post_is_in_db_with_old_timestamp(link,i):
                    posts_to_skip.append(link)
                else:
                    posts_to_print.append(link)
                
            
                
            #
            # output all of the new posts
            #
            for link in posts_to_print[:self.max_links]:
                self.feed_links[self.feed_name[i]].append(link)
               
   
class aggregator:
    def __init__(self):
        pass
    def getLinksFromRetriever(self):
        dbc = dbCurator()
        r = retriever()
        r.Retriever2Aggregator(dbc)
        for i in range(0,len(r.feed_name)):        
            #print r.feed_links[r.feed_name[i]]
            dbc.write2db(r.feed_links[r.feed_name[i]],i)
        return r.feed_links
        

class dbCurator:
    def __init__(self):
        self.db = ['feeds_FP.txt','feeds_DH.txt','feeds_CNN.txt']
        self.limit = 12 * 3600 * 1000
        self.current_time_millis = lambda: int(round(time.time() * 1000)) #function to get the current time
        self.current_timestamp = self.current_time_millis()
    
    def post_is_in_db(self,link,i):
        with open(self.db[i], 'r') as database:
            for line in database:
                if link in line:
                    return True
        return False
    
    # return true if the title is in the database with a timestamp > limit
    def post_is_in_db_with_old_timestamp(self,link,i):
        with open(self.db[i], 'r') as database:
            for line in database:
                if link in line:
                    ts_as_string = line.split('|', 1)[1]
                    ts = long(ts_as_string)
                    if self.current_timestamp - ts > self.limit:
                        return True
        return False
    
    def write2db(self,posts_to_print,i):
        #
            # add all the posts we're going to print to the database with the current timestamp
            # (but only if they're not already in there)
            #
        f = open(self.db[i], 'a')
        for link in posts_to_print:
            if not self.post_is_in_db(link,i):
                f.write(link + "|" + str(self.current_timestamp) + "\n")
        f.close
        
    
class lsa:
    def __init__(self):
        self.stopwords = stopwords
        self.ignorechars = punctuations
        self.wdict = {}
        self.dcount = 0 
        self.topNdict = {}
        self.headlines = []
        self.N = 5 #for top 5 headlines
        
    def get_only_text(self,url):
        """ 
            return the title and the text of the article
            at the specified url
        """
        page = urllib2.urlopen(url).read()
        soup = BeautifulSoup(page)
        text = ' '.join(map(lambda p: p.text, soup.find_all('p')))
        return soup.title.text, text
        
    def get_only_text_hindu(self,url):
        """ 
            return the title and the text of the article
            at the specified url
        """
        page = urllib2.urlopen(url).read()
        soup = BeautifulSoup(page)
        text = ' '.join(map(lambda p: p.text, soup.find_all('p','body')))
        return soup.title.text, text
        
    def get_only_text_TOI(self,url):
        """ 
            return the title and the text of the article
            at the specified url
        """
        page = urllib2.urlopen(url).read()
        soup = BeautifulSoup(page)
        text = ' '.join(map(lambda p: p.text, soup.find_all('arttextxml')))
        return soup.title.text, text
    			
        
    def parse(self, doc, title):
        title.replace(':','')
        words = doc.split()+title.split()
        #print title
        for w in words:
            w = w.encode('ascii','ignore').lower().translate(None, self.ignorechars)
            if w in self.stopwords:
                continue
            elif w in self.wdict:
                self.wdict[w].append(self.dcount)
            else:
                self.wdict[w] = [self.dcount]
        self.dcount += 1
        
    def build(self):
        self.keys = [k for k in self.wdict.keys() if len(self.wdict[k]) > 1]
        self.keys.sort()
        self.A = zeros([len(self.keys), self.dcount])
        for i, k in enumerate(self.keys):
            for d in self.wdict[k]:
                self.A[i,d] += 1
	
    def printA(self):
        print self.A
        
    def TFIDF(self):
        WordsPerDoc = sum(self.A, axis=0)
        DocsPerWord = sum(asarray(self.A > 0, 'i'), axis=1)
        rows, cols = self.A.shape
        for i in range(rows):
            for j in range(cols):
                self.A[i,j] = (self.A[i,j] / WordsPerDoc[j]) * log(float(cols) / DocsPerWord[i])
    def calc(self):
        self.U, self.S, self.Vt = svd(self.A)
    
    def printSVD(self):
        print 'Here are the singular values'
        print self.S
        print 'Here are the first 3 columns of the U matrix'
        print -1*self.U[:, 0:3]
        print 'Here are the first 3 rows of the Vt matrix'
        print -1*self.Vt[0:3, :]
    
    def get_cosine(self,vec1, vec2):
         #intersection = set(vec1.keys()) & set(vec2.keys())
        numerator = sum([vec1[x] * vec2[x] for x in range(0,len(vec1))])
        sum1 = sum([vec1[x]**2 for x in range(0,len(vec1))])
        sum2 = sum([vec2[x]**2 for x in range(0,len(vec2))])
        denominator = math.sqrt(sum1) * math.sqrt(sum2)
    
        if not denominator:
            return 0.0
        else:
            return abs (float(numerator) / denominator)
    def remove_text(self, text):
        sentences = text.split('.')
        filtered_sents = '. '.join([i for i in sentences if 'The Teams' not in i and 'wk' not in i])
        return filtered_sents
        
    def getScore(self, article_url_1, article_url_list,flag):
        
        title1, text1 = self.get_only_text(article_url_1)
        text1 = self.remove_text(text1)
        self.parse(text1,title1)
        
        for article_url_2 in article_url_list:      
            if flag==1:
                title, text = self.get_only_text_hindu(article_url_2)
                text = self.remove_text('text')
                
            else:
                title, text = self.get_only_text_TOI(article_url_2)
                text = self.remove_text('text')
                x = text.split('.')
                text =  '. '.join(x)
            self.headlines.append(title)
            self.parse(text,title)
        
        self.build()
        self.calc()
        rows, cols = self.Vt.shape
        for index in range(1,cols):
            self.topNdict[str(index-1)] = self.get_cosine( -1*self.Vt[0:rows, 0],  -1*self.Vt[0:rows, index])
        sorted_dict = sorted(self.topNdict.items(), key=operator.itemgetter(1), reverse=True)
#        for i in range(0,self.N):
#            key, value = sorted_dict[i]
#            print "rank "+str(i), self.headlines[int(key)]
#            print article_url_list[int(key)]
#            print "==================================================="
        key, value = sorted_dict[0]
        return self.headlines[int(key)], article_url_list[int(key)], value
    
        
class FrequencySummarizer:
    def __init__(self, min_cut=0.1, max_cut=0.9):
        """
         Initilize the text summarizer.
         Words that have a frequency term lower than min_cut 
         or higer than max_cut will be ignored.
        """
        self._min_cut = min_cut
        self._max_cut = max_cut 
        self._stopwords = set(stopwords + list(punctuations))
    
    def _compute_frequencies(self, word_sent):
        """ 
          Compute the frequency of each of word.
          Input: 
           word_sent, a list of sentences already tokenized.
          Output: 
           freq, a dictionary where freq[w] is the frequency of w.
        """
        freq = defaultdict(int)
        for s in word_sent:
            for word in s:
                if word not in self._stopwords:
                    freq[word] += 1
        # frequencies normalization and fitering
        m = float(max(freq.values()))
        for w in freq.keys():
            freq[w] = freq[w]/m
            if freq[w] >= self._max_cut or freq[w] <= self._min_cut:
                del freq[w]
        return freq
    
    def remove_hashtags(text):
        for sents in re.split(r' *[\.\?!][\'"\)\]]* *', text):
            sents = ' '.join(i for i in sents.split() if '#' not in i)
        return ' '.join
    def summarize(self, text, n):
        """
          Return a list of n sentences 
          which represent the summary of text.
        """
        sents = sent_tokenize(text)
        #sents = remove_hasttags(sents)        
        #assert n <= len(sents)
        word_sent = [word_tokenize(s.lower()) for s in sents]
        self._freq = self._compute_frequencies(word_sent)
        ranking = defaultdict(int)
        for i,sent in enumerate(word_sent):
            for w in sent:
                if w in self._freq:
                    ranking[i] += self._freq[w]
        sents_idx = self._rank(ranking, n)    
        return [(sents[j],ranking[j]) for j in sents_idx]
    
    def _rank(self, ranking, n):
        """ return the first n sentences with highest ranking """
        return nlargest(n, ranking, key=ranking.get)
        
    def get_only_text(self,url):
        """ 
            return the title and the text of the article
            at the specified url
        """
        page = urllib2.urlopen(url).read()
        soup = BeautifulSoup(page)
        text = ' '.join(map(lambda p: p.text, soup.find_all('p')))
        return soup.title.text, text
        
    def get_only_text_hindu(self,url):
        """ 
            return the title and the text of the article
            at the specified url
        """
        page = urllib2.urlopen(url).read()
        soup = BeautifulSoup(page)
        text = ' '.join(map(lambda p: p.text, soup.find_all('p','body')))
        return soup.title.text, text
    
    def get_only_text_toi(self,url):
        """ 
            return the title and the text of the article
            at the specified url
        """
        page = urllib2.urlopen(url).read()
        soup = BeautifulSoup(page)
        text = ' '.join(map(lambda p: p.text, soup.find_all('arttextxml')))
        return soup.title.text, text
        
class summarizer:
    def __init__(self, link, flag):
        self.article_url = link
        self.fs = FrequencySummarizer()
        self.flag = flag
        
    def remove_text(self, text):
        sentences = text.split('.')
        filtered_sents = '. '.join([i for i in sentences if 'The Teams (From):' not in i and '(wk)' not in i])
        return filtered_sents

    def call_summarizer(self,sentence):
        if self.flag==1:
            
            if 'deccanherald' in self.article_url:
                #index = text.find('Go to Top')
                #text = text[0:index]
                title, text = self.fs.get_only_text(self.article_url)
                text = self.remove_text(text)
                x = text.split('.')
                text =  '. '.join(x)
            if 'hindustantimes' in self.article_url:
                #index = text.find('Go to Top')
                #text = text[0:index]
                title, text = self.fs.get_only_text(self.article_url)
                text = self.remove_text(text)
                x = text.split('.')
                text =  '. '.join(x)
            if 'firstpost' in self.article_url:
                title, text = self.fs.get_only_text(self.article_url)
                text = self.remove_text(text)
                x = text.split('.')
                text =  '. '.join(x[1:])
                index = text.find('more in Sports')
                text = text[0:index]
            if 'thehindu' in self.article_url:
                title, text = self.fs.get_only_text_hindu(self.article_url)
                text = self.remove_text(text)
                
        else:
            title, text = self.fs.get_only_text_toi(self.article_url)
            text = self.remove_text(text)
            x = text.split('.')
            text =  '. '.join(x) 
        #print '----------------------------------'
        #print title
        #print text
        return self.fs.summarize(text, 2)[sentence]
        
class appender:
    def __init__(self):
        pass
    
class main:
    def __init__(self):
        self.To_summarize_links = []
        self.summarized_text = []
        
    def test(self):
        a = aggregator()
        links = a.getLinksFromRetriever()
        #print links
        for i in links['DH']:        
            newsLsa = lsa()
            headline_1, article_url_1,score1 = newsLsa.getScore(i, links['FP'],1)
            newsLsa = lsa()
            headline_2, article_url_2,score2 = newsLsa.getScore(i, links['CNN'],2)
            print i, article_url_1, score1, article_url_2, score2
            #print headline_1
            #print len(links['FP']), len(links['CNN'])
            if score1 > score2:
                self.To_summarize_links.append([i,article_url_1,score1,1,1])
                links['FP'].remove(article_url_1)
            else:
                self.To_summarize_links.append([i,article_url_2,score2,1,2]) #2 is flag for api
                links['CNN'].remove(article_url_2)
            #print len(links['FP']), len(links['CNN'])
        for link_list in self.To_summarize_links:
            summary = []
            score = 0.0
            for i in range(0,2):
                s = summarizer(link_list[i],link_list[i+3])
                text,value = s.call_summarizer(0)
                #print text
                if i==0:
                    summary = summary+[text]
                    score += value
                else:
                    if text not in summary[0] and summary[0] not in text:
                        summary = summary+[text]
                        score += value
                    else:
                        text,value = s.call_summarizer(1)
                        summary = summary+[text]
                        score += value
            #print '*', summary.decode('ascii','ignore'), score
            summarized_text = ' *' + '\n *'.join(summary)
            self.summarized_text.append((summarized_text,score))
        return self.summarized_text
        
m = main()
summarized_news =  m.test()
for news,score in summarized_news:
    print '----------------------------------'
    print news,score
    