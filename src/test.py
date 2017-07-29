from naiveBayesClassifier import tag_prob
from spell_check import correct_Sent
from ChatBot2 import ChatBot2
c = ChatBot2()

while True:
    print "Enter your message:",
    msg = raw_input()
    if msg == 'quit':
        break
    message = correct_Sent(msg)
    Username, Placename = c.getPlaceName(message)
    category, score = tag_prob(message,cl)
    if c.removeEntities(message,Username, Placename) =='':
        subCategory, intent = '',''
    else:
        subCategory, intent = c.findSubcategory(c.removeEntities(message,Username, Placename),category)
    print {'Username':Username,'Placename':Placename,'subCategory':subCategory,'intent':intent,'category':category,'score':score}