from nltk.tag.stanford import StanfordNERTagger

import os

class NamedEntitiesStanford:
    def __init__(self):
        self.abs_path = os.path.dirname(os.path.abspath('__file__')) 

    def GetEntities(self, TEXT):
        st = StanfordNERTagger(self.abs_path + '/../data/english.all.3class.distsim.crf.ser.gz',self.abs_path + '/../data/stanford-ner.jar')
        #TEXT = 'Ramesha wants beauty service at Domlur from Kormangala Parlour'
        l = st.tag(TEXT.split())
        loc = [t for t in TEXT.split() for a,b in l if b== 'LOCATION' and a.encode('ascii','ignore').lower()==t.lower()]
        org = [t for t in TEXT.split() for a,b in l if b== 'ORGANIZATION' and a.encode('ascii','ignore').lower()==t.lower()]
        per = [t for t in TEXT.split() for a,b in l if b== 'PERSON' and a.encode('ascii','ignore').lower()==t.lower()]
        return loc,org,per