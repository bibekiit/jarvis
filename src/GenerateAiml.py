# -*- coding: utf-8 -*-
"""
Created on Mon Nov  9 13:15:08 2015

@author: bibekbehera
"""

import os
import aiml

def write2aiml(f, pattern, template):
    f.write("\t<category>\n\t\t<pattern>"+pattern+" *</pattern>\n\t\t<template>\n\t\t\t"+template+"\n\t\t</template>\n\t</category>\n")

#Generate the std-startup.xml
Initiator = 'std-startup2.xml'
AimlFile = 'tmp.aiml'
with open(Initiator,'w') as f:
    f.write("""<?xml version="1.0" encoding="UTF-8"?>
<aiml>
    <!-- std-startup.xml -->

    <!-- Category is an atomic AIML unit -->
    <category>

        <!-- Pattern to match in user input -->
        <!-- If user enters "LOAD AIML B" -->
        <pattern>LOAD AIML B</pattern>

        <!-- Template is the response to the pattern -->
        <!-- This learn an aiml file -->
        <template>
            <learn>"""+AimlFile+"""</learn>
            <!-- You can add more aiml files here -->
            <!--<learn>more_aiml.aiml</learn>-->
        </template>

    </category>

</aiml>""")

#Generate aiml file

def generateAiml(AimlFile):
    with open(AimlFile,'w') as f:
        f.write("""<?xml version="1.0" encoding="UTF-8"?>
    <!-- basic_chat.aiml -->
    <aiml>""")
        write2aiml(f,"HELLO","Well, hello!")
        f.write("</aiml>")
        

