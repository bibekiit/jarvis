import cPickle
from logger import logger

import os

abs_path = os.path.dirname(os.path.abspath('__file__'))

class TextAnalytics:
        
    def __init__(self):
        logger.info("JARVIS2: Loading the classifier. This should take less than a minute...")
        with open(abs_path + "/../data/tagged_data_classifier.pkl", 'rb') as fid:
            cl = cPickle.load(fid)
        self.cl = cl

    def getCl(self):
        return self.cl