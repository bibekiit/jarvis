# -*- coding: utf-8 -*-
"""
Created on Mon Nov  9 17:53:55 2015

@author: bibekbehera
"""

import aiml,os
#from AimlQueryGenerator import query
from BasicGreeting import GetBasicGreeting
from UserName import GetUserName
from CityName import GetCityName
from NamedEntitiesStanford import GetEntities
from naiveBayesClassifier import tag_prob
from getInfo import GetSubCategory
import cPickle

intent_dict = {'food-and-beverages':'deliver','laundry':'clean','baby-products':'buy','pet-supplies':'buy','clothing-and-accessories':'buy','electronics':'buy','govt-services':'give','utility-and-bills':'recharge','grocery-and-gourmet-food':'deliver', 'travel-and-tickets':'book', 'general':'enquire', 'home-services': 'provide', 'beauty-services':'deliver'} 
def initiate_bot_brain():
    k = aiml.Kernel()
    
    #Training
    #k.learn("std-startup.xml")
    #k.respond("load aiml b")
    
    #Load bot's brain
    if os.path.isfile("bot_brain.brn"):
        k.bootstrap(brainFile = "bot_brain.brn")
    else:
        k.bootstrap(learnFiles = "std-startup.xml", commands = "load aiml b")
        k.saveBrain("bot_brain.brn")
    return k
    
def checkForOrderCompletion(d):
    l =[key for key in d if d[key]=='']
    if l==[]:
        return True, 'Order completed'
    else:
        return False, l[0]    
        
def completeOrder(d,session):
    for key in d:
        if d[key]=='' and key in session:
            d[key]=session[key]
    return d
def main2(cl):
    
    # 1.Extract user name from customer profile
    Username = GetUserName()
    
    # 2.Welcome message
    k = initiate_bot_brain()
    message = raw_input("Enter your message to the bot: ")
    
    
#    d = {u'customer': u'', u'destination': u'',u'source': u'',u'subCategory':u''}
    
#    #Chat initiation
#    while True:
#        Status, orderList = checkForOrderCompletion(d)
#        if Status:
#            print k.respond(orderList+' Mr '+d[u'customer'])
#            break
#        else:
#            print k.respond(orderList+" is not provided")
#            message = raw_input("Enter your message to the bot: ")
#            if k.respond(message)=='':
#                GeneratedAimlQuery,d = query(message)
#                print k.respond(GeneratedAimlQuery)
#            else:
#                print k.respond(message)
#            #print k.respond(message)
#            # Do something with bot_response
#            d = completeOrder(d,k.getSessionData()['_global'])
#            print d
#    while True:            
#        message = raw_input("Enter your message to the bot: ")
#        if message == "quit":
#            exit()
#        elif message == "save":
#            k.saveBrain("bot_brain.brn")
#        else:
#            print k.respond(message)
    
    #3. Authentication
    if Username != '':
        #4. find category
        category, score = tag_prob(message,cl)
        threshold = 0.8
        if score < threshold:
            GetBasicGreeting(k,"This is the welcome message for "+Username)
            message = raw_input("Enter your message to the bot: ")
            category, score = tag_prob(message,cl)
            print category,score
            if score>threshold:
                try:
                    subCategory,intent = GetSubCategory(message)
                    #print subCategory,intent
                except UnboundLocalError:
                    pass                    
                    #print message, intent_dict[category]
            else:
                subCategory = 'NA'
                intent = 'NA'
        else:
            print category,score
            print k.respond("Category found at once "+Username)
            try:
                subCategory,intent = GetSubCategory(message)
                #print subCategory,intent
            except UnboundLocalError:
                subCategory = message
                intent = intent_dict[category]                
                #print subCategory,intent
        Cityname = GetCityName()
        print k.respond("City confirmation message "+Cityname)
        message = raw_input("Enter your message to the bot: ")
        print k.respond(message)
    else:
        #4. find category
        print Username
        category, score = tag_prob(message,cl)
        print category,score
        threshold = 0.8
        if score < threshold:
            print k.respond("This is the second welcome message for authentication")
            message = raw_input("Enter your message to the bot: ")
            Place,_,Names = GetEntities(message)
            if Place==[]:            
                Username = Names[0:len(Names)-1]
                Cityname = Names[-1]
                if 'Bangalore' in Username or 'Hyderabad' in Username:
                    Username = Names[1:]
                    Cityname = Names[0]
            else:
                Cityname = Place[0]
                Username = Names
            print k.respond("Ask "+Username[0]+" what he wants")
            message = raw_input("Enter your message to the bot: ")
            category, score = tag_prob(message,cl)
            print category,score
            try:
                subCategory,intent = GetSubCategory(message)
                if subCategory == '':
                    subCategory = message
                #print subCategory,intent
            except UnboundLocalError:
                subCategory = message
                intent = intent_dict[category]                
                #print subCategory,intent
            
            print k.respond("Yes")
        else:
            print category,score
            print k.respond("This is the second welcome message for authentication")
            message2 = raw_input("Enter your message to the bot: ")
            Place,_,Names = GetEntities(message2)
            if Place==[]:            
                Username = Names[0:len(Names)-1]
                Cityname = Names[-1]
                if 'Bangalore' in Username or 'Hyderabad' in Username:
                    Username = Names[1:]
                    Cityname = Names[0]
            else:
                Cityname = Place[0]
                Username = Names
            #print Cityname, Username
            print k.respond("We know what "+Username[0]+" wants")
            try:
                subCategory,intent = GetSubCategory(message)
                #print subCategory,intent
            except UnboundLocalError:
                subCategory = message
                intent = intent_dict[category]                
                #print subCategory,intent
            print k.respond("Direct him to the agent")
    if type(Username)==list:
        Username = ' '.join(Username)
    print {'category':{'type':category,'score':score},'subCategory':{'type':subCategory,'intent':intent},'Username':Username, 'Cityname':Cityname}