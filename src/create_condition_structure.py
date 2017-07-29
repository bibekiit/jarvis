# -*- coding: utf-8 -*-
"""
Created on Mon Dec 14 15:28:27 2015

@author: bibekbehera
"""

stack = ['routing','email','name','intent','welcome']

def write2aiml(f, pattern, template):
    f.write("\t<category>\n\t\t<pattern>\n\t\t\t"+pattern+" \n\t\t</pattern>\n\t\t<template>\n\t\t\t"+template+"\n\t\t</template>\n\t</category>\n")

def print_order_stack(x, unknown):
    s=""
    if x==[] and not unknown:
        s = ' order complete'
    else:
        for i in x:
            s = s + " " +i+ " unknown"
    return s
    
def print_path(x, unknown, known, pop_or_remove_condition,n,f):
    for i in range(0,len(x)):
        
        if pop_or_remove_condition != 'status_dict.pop()':
            pop_or_remove =  pop_or_remove_condition + "('"+x[i]+"')"
        else:
            pop_or_remove = pop_or_remove_condition
        #print x[i+1:]
        
        if i==len(x)-1:
            tab_string = ''.join(['    ']*(i+n))
            tab_string2 = ''.join(['    ']*(i+n+1))
            print tab_string + "if "+x[i]+":"
            print tab_string2 + pop_or_remove
            if known and unknown:
                response = x[0]+" + ' "+known+" + ' "+unknown+" unknown"+print_order_stack(x[i+1:],unknown)
                response2 = "*" + "' "+known+" + ' "+unknown+" unknown"+print_order_stack(x[i+1:],unknown)
            else:
                if known:
                    response = x[0]+" + ' "+known+" + ' "+print_order_stack(x[i+1:],unknown)
                    response2 = "*" + "' "+known+" + ' "+print_order_stack(x[i+1:],unknown)
                if unknown:
                    response = x[0]+" + ' "+unknown+" unknown"+print_order_stack(x[i+1:], unknown)
                    response2 = "*" + "' "+unknown+" unknown"+print_order_stack(x[i+1:], unknown)
                else:
                    response = x[0]+" + ' "+print_order_stack(x[i+1:],unknown)
                    response2 = "*" + "' "+print_order_stack(x[i+1:],unknown)
            
            print tab_string2 + "return k.respond("+response+"'), status_dict"
            print tab_string + "else:"
            write2aiml(f,' '.join(response2.replace("'",'').replace("+",'').upper().split()),'here * is '+x[0])
            if len(x)>1:            
                if known and unknown:
                    response = x[0]+" + ' "+known+" + ' "+unknown+" unknown"+print_order_stack(x[i:],unknown)
                    response2 = "*" + "' "+known+" + ' "+unknown+" unknown"+print_order_stack(x[i:],unknown)
                else:
                    if unknown:
                        response = x[0]+" + ' "+unknown+" unknown"+print_order_stack(x[i:],unknown)
                        response2 = "*" + "' "+unknown+" unknown"+print_order_stack(x[i:],unknown)
                    elif known:
                        response = x[0]+" + ' "+known  +" + ' "+print_order_stack(x[i:],unknown)
                        response2 = "*" + "' "+known  +" + ' "+print_order_stack(x[i:],unknown)
                    else:
                        response = x[0]+" + ' " + print_order_stack(x[i:],unknown)
                        response2 = "*" + "' " + print_order_stack(x[i:],unknown)
            else:
                if known and unknown:
                    response = "' "+known+" + ' "+unknown+" unknown"+print_order_stack(x[i:],unknown)
                    response2 = "' "+known+" + ' "+unknown+" unknown"+print_order_stack(x[i:],unknown)
                else:
                    if unknown:
                        response = "' "+unknown+" unknown"+print_order_stack(x[i:],unknown)
                        response2 = "' "+unknown+" unknown"+print_order_stack(x[i:],unknown)
                    elif known:
                        response = "' "+known  +" + ' "+print_order_stack(x[i:],unknown)
                        response2 = "' "+known  +" + ' "+print_order_stack(x[i:],unknown)
                    else:
                        response = print_order_stack(x[i:],unknown)
                        response2 = print_order_stack(x[i:],unknown)
            print tab_string2 + "k.respond("+response+"'), status_dict"
            write2aiml(f,' '.join(response2.replace("'",'').replace("+",'').upper().split()),'here * is '+x[0])
                    
        else:
            tab_string = ''.join(['    ']*(i+n))
            tab_string2 = ''.join(['    ']*(i+n+1))
            print tab_string + "if "+x[i]+":"
            print tab_string2 + pop_or_remove
    #print x, known
    for j in range(1,len(x)-1):
        #print "correct response"
        if len(x)>1:
            if known and unknown:
                response = x[0]+" + ' "+known+" + ' "+unknown+" unknown"+print_order_stack(x[len(x)-1-j:], unknown)
                response2 = "*" + "' "+known+" + ' "+unknown+" unknown"+print_order_stack(x[len(x)-1-j:], unknown)
            else:
                if known:
                    response = x[0]+" + ' "+known+" + ' "+print_order_stack(x[len(x)-1-j:],unknown)
                    response2 = "*" + "' "+known+" + ' "+print_order_stack(x[len(x)-1-j:],unknown)

                elif unknown:
                    response = x[0]+" + ' "+unknown+" unknown"+print_order_stack(x[len(x)-1-j:],unknown)
                    response2 = "*" + "' "+unknown+" unknown"+print_order_stack(x[len(x)-1-j:],unknown)
                else:
                    response = x[0]+" + '"+print_order_stack(x[len(x)-1-j:],unknown)
                    response2 = "*" + "'"+print_order_stack(x[len(x)-1-j:],unknown)
        else:
            if known and unknown:
                response = "' "+known+" + ' "+unknown+" unknown"+print_order_stack(x[len(x)-1-j:],unknown)
                response2 = "' "+known+" + ' "+unknown+" unknown"+print_order_stack(x[len(x)-1-j:],unknown)
            else:
                if known:
                    response = "' "+known+" + ' "++print_order_stack(x[len(x)-1-j:],unknown)
                    response2 = "' "+known+" + ' "++print_order_stack(x[len(x)-1-j:],unknown)
                elif unknown:
                #print "correct response"
                    response = "' "+unknown+" unknown"+print_order_stack(x[len(x)-1-j:],unknown)
                    response2 = "' "+unknown+" unknown"+print_order_stack(x[len(x)-1-j:],unknown)
                else:
                    response = "'"+print_order_stack(x[len(x)-1-j:],unknown)
                    response2 = "'"+print_order_stack(x[len(x)-1-j:],unknown)
            
        tab_string = ''.join(['    ']*(len(x)-1-j+n))
        tab_string2 = ''.join(['    ']*(len(x)-1-j+n+1))
        print tab_string + "else:"
        print tab_string2 + "k.respond("+response+"'), status_dict"
        write2aiml(f, ' '.join(response2.replace("'",'').replace("+",'').upper().split()), "* means here "+x[0])
    j = len(x)-1
    tab_string = ''.join(['    ']*(len(x)-1-j+n))
    if len(x)>1:
        print tab_string + "else:"
        return x[0]
    else:
        return x[0]

def print_path_all_possibilities_from_known(x, known,n,f):
    unknown = ''
    for i in range(0,len(x)):
        no_of_tabs = n+i
        if i==0:
            unknown += ' ' + print_path(x, unknown, known, 'status_dict.pop()',no_of_tabs,f)
        else:
            unknown += ' ' + print_path(x[i:], unknown, known, 'status_dict.remove',no_of_tabs,f)
def print_path_all_possibilities_from_given_Stack(x,f):
    for i in range(0,len(x)):
        if i==0:
            new_stack = x[0:len(x)-1-i]
            new_stack.reverse()
        
            print "    " + "if status_dict[-1]=='"+x[len(x)-1-i]+"':"
            print "        " + "status_dict.pop()"
            print_path_all_possibilities_from_known(new_stack,x[len(x)-1-i] + " done'",3,f)
            
        else:
            new_stack = x[0:len(x)-i]
            new_stack.reverse()
        
            print "    " + "elif status_dict[-1]=='"+x[len(x)-1-i]+"':"
            print_path_all_possibilities_from_known(new_stack,'',2,f)
        
def generateAiml(AimlFile):
    with open(AimlFile,'w') as f:
        f.write("""<?xml version="1.0" encoding="UTF-8"?>
                    <!-- basic_chat.aiml -->
                    <aiml>""")
        print_path_all_possibilities_from_given_Stack(stack,f)

        f.write("</aiml>")
        
generateAiml('tmp1.aiml')
