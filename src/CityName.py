# -*- coding: utf-8 -*-
"""
Created on Tue Nov 24 13:10:55 2015

@author: bibekbehera
"""

import os

class CityName:
    def __init__(self):
        self.abs_path = os.path.dirname(os.path.abspath('__file__')) 

    def GetCities(self):
        d =[]
        f = open(self.abs_path+'/../data/cities_and_towns.csv','rb')
        for row in f:
            l = row.split(',')
            d.append(l[1])
        return d
        
        
    def CheckCityName(self,Text):
        
        citynames = self.GetCities()
        for city in citynames:
            if city in Text:
                return True, city
        return False, ''
    
