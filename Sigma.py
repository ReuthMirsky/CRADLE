class Letter(object):
    def __init__(self, ch='', params=[]):
         
            self._ch=ch                 # Type string
            
            self._params=[]         # Type list of tuples <paramName, paramVal> with initial value None 
            for param in params:
                if type(param)==tuple:
                    self._params.append(param)
                else:
                    self._params.append((param, None))
    
        
    def get(self):
        return self._ch
    
    def __repr__(self):
        res = '<' + self.get() + ' '
        if self._params==[]:
            res += '/>'
        else:
            #res += '<'
            for param in self._params:
                #val = param[1] if (param[1]!=None) else 'None'
                #if param[0] != 'scd' and  param[0] !='dcd' and  param[0] !='rcd':
                res += str(param[0]) + '=\"' + str(param[1]) + "\", "
            res = res[:-2]
            res += '/>'
        return res
    
    def getParam(self, name): 
        if name==None or self._params==[]:
            return None
        for pair in self._params:
            if pair[0]==name:
                return pair[1]
       
    def setParam(self, name, val): 
        if name==None or self._params==[]:
            return None
        for paramIndex in range(len(self._params)):
            param = self._params[paramIndex]
            if param[0] == name:
                self._params[paramIndex] = (name,val)
        return None
    
    def getParamName(self, index):
        return self._params[index][0];
    
    def getParamVal(self, index):
        return self._params[index][1];
    
    def getParamList(self):
        return self._params
    
    def hasParam(self, other_name):
        for param in self._params:
            if param[0]==other_name:
                return True
        return False

    def matchLetter(self, letter):
        if letter.get()==self.get() and self.matchTerminalLetterParams(letter):
            return True
        return False
    
    def matchTerminalLetterParams(self, obs):
        for (name, val) in self._params:
            if val!=None:
                if obs.getParam(name)!=None and obs.getParam(name)!=val:
                    return False
        return True   

#Class for Terminal letters    
class Sigma(Letter):
    _type='Sigma'

#Class for Non-terminal letters
class NT(Letter):
    _type='NT'
