# -*- coding: utf-8 -*-
"""
Created on Mon Feb  8 13:09:12 2016

@author: bibekbehera
"""
import networkx as nx
from mood_finder import create_list_of_transitions

class train_fsm():
    def __init__(self):
        self.transitions = {}
        self.states = ['S1']
        pass
    
    def addTransitions(self,curr_transition,next_transition):
        if curr_transition not in self.transitions.keys():
            self.transitions[curr_transition] = {next_transition:0}
            self.transitions[curr_transition][next_transition] += 1
        else:
            if next_transition not in self.transitions[curr_transition].keys():
                self.transitions[curr_transition][next_transition] = 1
            else:
                self.transitions[curr_transition][next_transition] += 1
    
    def getTransitions(self,listOfTransitions):
        for i in range(1, len(listOfTransitions)):
            self.addTransitions(listOfTransitions[i-1], listOfTransitions[i])
        
    def normalizeTransitionWeights(self):
        for i in self.transitions.keys():
            total = sum(self.transitions[i].values())
            for j in self.transitions[i].keys():
                self.transitions[i][j] = self.transitions[i][j]/float(total)
                #print self.transitions[i][j]
                
    
    def generateStateDiagram(self):
        lines = []
        for i in self.transitions.keys():
            for j in self.transitions[i].keys():
                lines.append(str(ord(i)-ord('A'))+" "+str(ord(j)-ord('A'))+" "+str(self.transitions[i][j]))
        self.stateDiagram = nx.parse_edgelist(lines, nodetype = int, data=(('weight',float),))  
        
class test():
    def __init__(self):
        self.mood_dict = {'indicative':'A', 'imperative':'B', 'conditional':'C', 'subjunctive':'D'}
        
    def map_moods_to_state(self, l):
        #takes a list of moods and convert mood as per mapping
        print l
        l_mapped = [self.mood_dict[i] for i in l]
        return l_mapped
        
    def main(self):
        mood_list = create_list_of_transitions()
        print mood_list
        mood_mapped_list = [self.map_moods_to_state(i) for i  in mood_list[1:]]
        tf = train_fsm()
        for i in mood_mapped_list:
            tf.getTransitions(i)
        tf.normalizeTransitionWeights()
        print tf.transitions
        tf.generateStateDiagram()
        print tf.stateDiagram.nodes()
        print tf.stateDiagram.edges(data=True)
    
    
        
        
    