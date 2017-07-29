import sys
reload(sys)
sys.setdefaultencoding("ISO-8859-1")
import nltk, re
from nltk.corpus import stopwords
from nltk.stem.snowball import SnowballStemmer
import cPickle

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
    
def sentenceClassifier(text,cl):
    modified_sent = tokenize_only(remove_stopwords(text))
    prob_dist = cl.prob_classify(modified_sent)
    tag = prob_dist.max()
    return tag, round(prob_dist.prob(tag), 2)

def tag_prob(text,cl):
    tag,prob = sentenceClassifier(text,cl)
    return tag,prob
        
def main(text):
    with open('/Users/bibekbehera/my_dumped_classifier_afterStemming.pkl', 'rb') as fid:
        cl = cPickle.load(fid)
    stemmer = SnowballStemmer("english")
    stopwords = nltk.corpus.stopwords.words('english')
    print tag_prob(text, cl) 

#s = 'Please book a flight from Bengaluru to Bhubaneshwar'
#main(s)
    
