#n = raw_input()

import re, collections
from UserName import UserName
from CityName import CityName

def words(text): return re.findall('[a-z]+', text.lower()) 

def train(features):
    model = collections.defaultdict(lambda: 1)
    for f in features:
        model[f] += 1
    return model

NWORDS = train(words(file('../data/big.txt').read()))
NWORDS_citynames = train(words(file('../data/city.txt').read()))

alphabet = 'abcdefghijklmnopqrstuvwxyz'

def edits1(word):
   splits     = [(word[:i], word[i:]) for i in range(len(word) + 1)]
   deletes    = [a + b[1:] for a, b in splits if b]
   transposes = [a + b[1] + b[0] + b[2:] for a, b in splits if len(b)>1]
   replaces   = [a + c + b[1:] for a, b in splits for c in alphabet if b]
   inserts    = [a + c + b     for a, b in splits for c in alphabet]
   return set(deletes + transposes + replaces + inserts)

def known_edits2(word,db):
    return set(e2 for e1 in edits1(word) for e2 in edits1(e1) if e2 in db)

def known(words,db): return set(w for w in words if w in db)

def correct(word,db):
    candidates = known([word],db) or known(edits1(word),db) or known_edits2(word,db) or [word]
    return max(candidates, key=db.get)
    
def correct_Sent(sent):
    mod_sent = []
    u = UserName()
    c = CityName()    
    for word in sent.split():
        if u.CheckPersonName(word.capitalize()):
            l = word.capitalize()
        elif c.CheckCityName(word.capitalize()):
            l = word.capitalize()
        else:
            l = correct(word,NWORDS)
            
        if word[0].isupper():
            l = l.capitalize()
        mod_sent.append(l)
    return ' '.join(mod_sent)
