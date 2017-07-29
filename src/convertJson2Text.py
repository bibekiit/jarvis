# -*- coding: utf-8 -*-
"""
Created on Thu Nov  5 19:38:47 2015

@author: bibekbehera
"""

import ast
import json
import sys
reload(sys)
sys.setdefaultencoding("ISO-8859-1")

with open('/Users/bibekbehera/Downloads/test_restdata.json') as json_data:
    content = json_data.readlines()
d = ast.literal_eval(content[0])

for i in range(719,len(d["data"])):
    f = open('Res_data/Res'+str(i),'w')
    json_acceptable_string=d["data"][i].replace("\\\"","")
    print i
    d2 = json.loads(json_acceptable_string)
    for k in d2.keys():
        if type(d2[k]) != int:
            if len(d2[k])>0:
                f.write( k + '\n')
                f.write ('-------------------\n')
                f.write ('\t'.join(d2[k][0]) + '\n')
                f.write ('--------------------------------------------------------------\n')
                for k1 in d2[k]:
                    f.write('\t'.join([str(x).encode('cp1252') for x in k1.values()])+ '\n') #.encode('ascii','ignore'),.encode('cp1252')
                    
        else:    	
            f.write( str(d2[k])+ '\n')
    f.close()