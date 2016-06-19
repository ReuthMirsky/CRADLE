class Rule(object):
    ruleAmount=0

    def __init__(self, A, alpha=[], order=[], paramConst=[], pid=False):
        '''
        Constructor
        '''
        self._A=A                       #this item is either of type Sigma or NT
        self._alpha=alpha               #this is a list of NTs and Sigmas
        self._order=order               #each item in this list is (i,j) which means the ith child must come before the jth chikd
                                            #both i and j are of type int
        self._paramConst=paramConst     #each item in this list is (i,iname,j,jname) which means that the parameter iname of the ith child
                                        #must be equal to the parameter jname of the jth child (i or j equals -1 means that its the root)
        if pid:
            self._pid = pid
        else:    
            Rule.ruleAmount+=1
            self._pid=Rule.ruleAmount

    #Prints this rule                                
    def __repr__(self):
        res = self._A.get() + " -> "
        for child in self._alpha:
            res += child.get() + " "       
        res += "| [ "
        for cons in self._order:
            res += self.constraintWithLetters(cons)
        res += "]\n"
        res += "\t" + self.parameterConstraints()      
        return res
    
    #Returns a parameter using its name and value (string)
    def constraintWithLetters(self, cons):
        left = self._alpha[cons[0]].get()
        right = self._alpha[cons[1]].get()
        return "(" + left + "," + right + ") "

    #Returns all constraints for this rule (string)     
    def parameterConstraints(self):
        if self._paramConst==None:
            return "[]"
        res="[ "
        for cons in self._paramConst:
            if cons[0]==-1:
                res+= self._A.get() + "." + cons[1] + "=" +  self._alpha[cons[2]].get() + "." + (cons[3]) + " "
            elif cons[2]==-1:
                res+= self._alpha[cons[0]].get() + "." + cons[1] + "=" +  self._A.get() + "." + (cons[3]) + " "
            else:
                res+= self._alpha[cons[0]].get() + "." + cons[1] + "=" +  self._alpha[cons[2]].get() + "." + (cons[3]) + " "
        res+= "]"
        return res

# -------------------------------- Getters and Setters ------------------------------------------------
    #Return all constraints for this rule (a list of tuples, each tuple of the form (<index of child/-1>,<paramName>,<index of child/-1>,<paramName>)) 
    def getParamCons(self):
        return self._paramConst
        
    # Return all leftmost children of the rule
    # if byIndex is False, returns the child itself. If byIndex is True, returns its index number    
    def leftMostChilds(self, byIndex=False):
        res = []
        i=0
        
        if self._alpha == None:
            return []
        
        for ch in self._alpha:            
            if not self.hasConstraint(i):
                if byIndex:
                    res.append(i)
                else:
                    res.append(ch)
            i+=1
                
        return res;
    
    # Return tuples of leftmost children with their index
    def leftMostChildsWithNums(self):
        res = []
        i=0
        
        if self._alpha == None:
            return []

        for ch in self._alpha:            
            if not self.hasConstraint(i):
                res.append((ch,i))
            i+=1
                
        return res;
    
    # Return all "right" children of the rule (children that are not leftmost)
    def rightChilds(self, byIndex=False):
        right = self._alpha[:] if not byIndex else list(range(len(self._alpha)))
        for ch in self.leftMostChilds(byIndex):
            right.remove(ch)
        return right
    
    # service function for leftmostChilds
    def hasConstraint(self, index):
        for cons in self._order:
            if cons[1] == index:
                return True;
        return False;
    
    #return a list of all order constraints limiting this child
    def allChildConstraints(self, index):
        res = []
        for cons in self._order:
            if cons[1] == index:
                res.append(cons[0])
        return res
           
    #return the first index of child in alpha (children's list), or throws an error if there is no such child
    def getChildIndex(self, child):
        return self._alpha.index(child)