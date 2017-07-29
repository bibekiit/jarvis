# -*- coding: utf-8 -*-
"""
Created on Tue Feb 16 13:05:04 2016

@author: bibekbehera
"""

class goal_fulfilment_maps:
    def __init__(self):
        self.order_fulfilment_list = {}
        self.reply = ""
    
    def greeting_response(self,category,intent):
        if intent=="":
            self.reply =  "Welcome to MagicXX"
        else:
            if self.order_fulfilment_list.has_key(category):
                for item in self.order_fulfilment_list[category].keys():
                    if self.order_fulfilment_list[category][item] == '':
                        self.order_fulfilment_list[category][item]=intent[item]
            else:
                self.order_fulfilment_list[category] = {}
                self.order_fulfilment_list[category] = intent
            for item in self.order_fulfilment_list[category]:
                unknown_item = self.order_fulfilment_list[category][item]                
                if unknown_item=="":
                    response = "Welcome to MagicXX. Sir what can i do for you"
                return response, item
            self.reply = "Welcome to MagicXX. " + "Do you want anything else?"
        return self.reply, ''
        
    def procedural_response(self, speech_act, category, intent):    
        if speech_act == "Ex":
            return "We are glad to serve you", ''
        elif speech_act == "De" or category!='':
            if self.order_fulfilment_list.has_key(category):
                for item in self.order_fulfilment_list[category].keys():
                    if self.order_fulfilment_list[category][item] == '':
                        self.order_fulfilment_list[category][item]=intent[item]
            else:
                self.order_fulfilment_list[category] = {}
                self.order_fulfilment_list[category] = intent
            for item in self.order_fulfilment_list[category]:
                unknown_item = self.order_fulfilment_list[category][item]                
                if unknown_item=="":
                    if item=='INTENT':
                        response = "Sir what can i do for you"
                    else:
                        response = "Yes Sir, please provide details regarding "+item
                    return response, item
            return "Do you want anything else sir", ''
        elif speech_act == "":
            return "Hello Sir, What may i do for you?", ''
    
    def recharge_gre(self,speech_act, intent):
        return self.greeting_response('recharge',intent)
        
    def recharge_inf(self):
        return "Yes we will give you the information"
        
    def recharge_pro(self,speech_act, intent):
        return self.procedural_response(speech_act, 'travel-and-tickets', intent)
        
    def recharge_dr(self):
        return "Welcome to MagicXX"
        
    def recharge_ts(self):
        return "Welcome to MagicXX"
        
    def recharge_end(self):
        return "Goodbye", ""
        
    def unb_gre(self,speech_act, intent):
        return self.greeting_response('utility-and-bills',intent)
        
    def unb_inf(self):
        return "Yes we will give you the information"
        
    def unb_pro(self,speech_act, intent):
        return self.procedural_response(speech_act, 'utility-and-bills', intent)
        
    def unb_dr(self):
        return "Welcome to MagicXX"
        
    def unb_ts(self):
        return "Welcome to MagicXX"
        
    def unb_end(self):
        return "Goodbye", ""
        
    def o_gre(self,speech_act, intent):
        return self.greeting_response('others',intent)
        
    def o_inf(self):
        return "Yes we will give you the information"
        
    def o_pro(self,speech_act, intent):
        return self.procedural_response(speech_act, 'others', intent)
        
    def o_dr(self):
        return "Welcome to MagicXX"
        
    def o_ts(self):
        return "Welcome to MagicXX"
        
    def o_end(self):
        return "Goodbye"
        