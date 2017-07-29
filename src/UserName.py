import os
class UserName:
    def __init__(self):
        self.abs_path = os.path.dirname(os.path.abspath('__file__')) 

    def GetNames(self):
        d =[]
        f = open(self.abs_path + '/../data/Babynames.csv','rb')
        for row in f:
            l = row.split('\n')
            d.append(l[0])
        return d
        
        
    def CheckPersonName(self,name):
        PersonNames = self.GetNames()
        if name.capitalize() in PersonNames:
            return True
        else:
            return False
    
    
