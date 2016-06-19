from copy import deepcopy
from Tree import Tree
from Sigma import NT, Sigma

#This class represents a plan library
class PL(object):
    
    def __init__(self, sigma, NT, R, P):
        '''
        Constructor
        '''
        self._Sigma = sigma     # list of Sigmas
        self._NT = NT           # list of NTs
        self._R = R             # subset of NT
        self._P = P             # list of rules
    
    #Prints the plan library        
    def __repr__(self):
        res = "Plan Library: \nSigma=" + self._Sigma.__repr__() + "\nNT=" + self._NT.__repr__() + "\nR=" + self._R.__repr__() + "\nRules="
        for rule in self._P:
            res += "\t" + rule.__repr__() + "\n"
        return res

#------------------------------ Getters and Setters ----------------------------------------------
    #Returns the goal symbols of this PL
    def getGoals(self):
        return self._R
    
    #Returns the probability of each goal symbol
    def getRootProb(self):
        return 1/len(self._R)

    #Returns the probability that a specific rule would be chosen
    #StartsWith is a constraint on what we can see on the left side of the rule
    def getRuleProb(self, startsWith=[]):
        if startsWith==[]:
            return 1/len(self.P)
        amountOfMatchingRules = 0.0
        for rule in self._P:
            if rule._A.get() == startsWith.get():
                amountOfMatchingRules += 1
        if amountOfMatchingRules == 0:
            return 0
        else:
            return 1/amountOfMatchingRules
        
# ---------------------------------- Methods ---------------------------------------------------------------
    
    #Returns the set of generating trees whose foot is observation and its root is the root of the tree from treesBeforeSubstitute 
    #treesBeforeSubstitute is a list of trees into which we want to combine the new observations
    #observation is the new action to be added
    def generatingSetForObs(self, treesBeforeSubstitute, observation):
        treesAfterSubstitute = []
        for tree in treesBeforeSubstitute:
            #If this is a leftmost tree, the result of footWithIndex will be of the form: (<node of foot>, <index> )
            footWithIndex = tree.isLeftMostTree(byIndex=True)
            #If this tree has a foot (must be true here, if false, it's a bug!) and if this foot matches the observation 
            if footWithIndex and footWithIndex[0].sameParameters(observation, '-1') :
                newCopy = tree
                #Update that this child was fulfilled so it no longer be considered an open frontier item 
                if newCopy.substitute(observation, footWithIndex[1]):
                    treesAfterSubstitute.append(newCopy)
        return treesAfterSubstitute
    
    #Returns the set of all possible generating trees with a root in generatingFrom
    #generatingFrom is a list of symbols which are the possible roots of the trees we're seeking
    def generatingSet(self, generatingFrom):
        #res is a set of all leftmost trees deriving from this PL which start with a root from R or NT
        res=[] 
        for goal in generatingFrom:
            for rule in self._P:
                if goal.matchLetter(rule._A):
                    for tree in self.createTrees(rule):
                        res.append(tree)
        return res                    

    #Returns all trees which can be generated from the rule "rule".
    #recursive is used for recursive calls of this function
    def createTrees(self, rule, recursive=0):
        #if rule has only one child 
        if 1 == len(rule._alpha):
            if rule._alpha[0]._type=='Sigma':
                child = Tree("Basic", rule._alpha[0], (), [], self)
                root = Tree("Complex", rule._A, rule, [child], self)
                return [root]
            else:
                return []
        
        #else, need to create all possible outcomes from tree
        trees=[]
        leftMostChilds = rule.leftMostChilds(byIndex=True)
        for childIndex in range(len(rule._alpha)):
            if childIndex in leftMostChilds:
                if type(rule._alpha[childIndex])==NT:
                    #collect all possible derivations of this child to childTrees
                    for childRule in self._P:
                        
                        childRecursion = recursive
                        #Make sure you're not entering a possibly infinite loop (Left recursion bounding)
                        if childRule._A == rule._A:
                            if childRecursion < 1:
                                childRecursion += 1
                            else:
                                return trees
                            
                        if rule._alpha[childIndex] == childRule._A:
                            #to create the tree, other children should be basic tree nodes
                            otherChildren=self.otherChildrenTrees(rule, childIndex)
                            #for each possible combination of children:
                            for singleOtherChildrenExp in otherChildren:
                                #add all current leftmostTrees to the list, under trees:
                                for tree in self.createTrees(childRule, childRecursion+1):
                                    allChildren = singleOtherChildrenExp
                                    allChildren.insert(childIndex,tree)
                                    root = Tree("Complex", rule._A, rule, allChildren, self)
                                    trees.append(root)  
                elif type(rule._alpha[childIndex])==Sigma:
                    tree = Tree("Basic", rule._alpha[childIndex], (), [], self)
                    #to create the tree, other children should be basic tree nodes
                    otherChildren=self.otherChildrenTrees(rule, childIndex)
                    #for each possible combination of children:
                    for singleOtherChildrenExp in otherChildren:
                        allChildren = singleOtherChildrenExp
                        allChildren.insert(childIndex,tree)
                        root = Tree("Complex", rule._A, rule, allChildren, self)
                        trees.append(root)  
        return trees
    
    #Returns all possible subtrees which can be generated from each child of rule which isn't the specialChild
    #rule is the rule we're creating trees by, and here we need to create the subtrees of every child but one
    #specialChild is the child with a "foot" that gets attended in "createTrees" so it does not require expansions here
    def otherChildrenTrees(self, rule, specialChild):
        res=[]
        i = 0;
        for child in rule._alpha:
            if i != specialChild:
                listOfPossibleTrees = self.childWithPossibleRules(child)
                if res==[]:
                    res=listOfPossibleTrees
                else:
                    completeRes = []
                    for singleExp in res:
                        for newTree in listOfPossibleTrees:
                            newExp = singleExp
                            newExp.extend(newTree)
                            completeRes.append(newExp)   
                    res = completeRes  
            i += 1       
        return res   

    #Returns a new tree node for child with all the possible rules it might fulfill in future observations
    #Child is the symbol we're trying to expand
    def childWithPossibleRules(self, child):
        res=[]
        if type(child)==Sigma:
            res.append([Tree("Basic", deepcopy(child), (), PL=self)])
        else:
            childRules = []            
            for rule in self._P:    #Collect all possible rules this child might be
                if rule._A == child:
                    childRules.append(rule)    
            res.append([Tree("Complex", deepcopy(child), childRules, PL=self)])
        return res