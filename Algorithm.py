from copy import deepcopy 
from Explanation import Explanation
from Sigma import Letter, Sigma
from NT import NT
from Rule import Rule
from Tree import Tree
import random
from math import log
import sys
import xml.etree.ElementTree as ET
import time
from Probes import *

# PL is the plan library for this run
# observations is a set of sigmas that needs to be explained
# Returns a list of explanations which explain observations according to the rules in PL
def ExplainAndCompute(PL, observations):
    
    #Init
    exps = []
    exps.append(Explanation())
    goalsGeneratingSet = PL.generatingSet(PL.getGoals())
    allGeneratingSet = {}
    for nt in PL._NT:
        allGeneratingSet[nt.get()] = PL.generatingSet([nt])
    
    TreeAvgBound = 2.0
    AgeAvg = 1.0
    FrontierAvg = 1.0
    

    #Loop over all observations
    obsNum = 1
    for obs in observations:   
        #Measures that will used to calculate filter's thresholds
        expsTemp = []
        treesTotal = 0
        probabilityTotal = 0.0
        ageTotal = 0
        frontierTotal = 0
        numOfExps = 0.0
        oldExpNum = 0
        
        #Measures for upper and lower bounds
        ProbabilityMin = 1.0
        ProbabilityMax = 0.0
        TreeAmountMin = 1000
        TreeAmountMax = 0
        AgeMin= 1000
        AgeMax = 0
        FrontierMin = 1000
        FrontierMax = 0

        #Main loop - given a new observation, try to combine it incrementally into explanations from previous observations                
        while not len(exps)==0:
            oldExpNum+=1
            currentExp = exps.pop()

            #Filter Explanations
            currentExpProb = currentExp.getExpProbability()
            currentExpSize = currentExp.getSize()
            currentExpAge = currentExp.getAge()
            currentExpFrontier = currentExp.getFrontierSize()

            #Measures for upper and lower bounds
            if currentExpProb < ProbabilityMin:
                ProbabilityMin = currentExpProb
            if currentExpProb > ProbabilityMax:
                ProbabilityMax = currentExpProb
            if currentExpSize < TreeAmountMin:
                TreeAmountMin = currentExpSize
            if currentExpSize > TreeAmountMax:
                TreeAmountMax = currentExpSize
            if currentExpAge < AgeMin:
                AgeMin = currentExpAge
            if currentExpAge > AgeMax:
                AgeMax = currentExpAge
            if currentExpFrontier < FrontierMin:
                FrontierMin = currentExpFrontier
            if currentExpFrontier > FrontierMax:
                FrontierMax = currentExpFrontier
            
            #Filter this explanation if is exceeds the threshold of some filter
            if currentExpSize > TreeAvgBound:
                continue
            if currentExpAge > AgeAvg:
                continue
            if currentExpFrontier > FrontierAvg:
                continue
           
            treeIndexInExp = 0
            #Consider all the existing plans the observation could extend
            for tree in currentExp.getTrees():
                treeFrontier = tree.getFrontier(withIndices=True)
                for (node, index) in treeFrontier:

                    # Try to complete the frontier if it is a terminal letter, same as currentObs
                    if tree.sameParameters(obs, index):
                        newCopy = deepcopy(tree)
                        if newCopy.substitute(obs, index):
                            newCopy.getDecendant(index)._isComplete = True
                            newExp = deepcopy(currentExp)
                            newExp.setTree(newCopy, treeIndexInExp)
                            newExp.updateLocalProbChoices(newCopy)
                            newExp.resetAge()
                            expsTemp.append(newExp)
                            numOfExps += 1
                            treesTotal += len(newExp.getTrees())
                            probabilityTotal += newExp.getExpProbability()
                            ageTotal += newExp.getAge()
                            frontierTotal += newExp.getFrontierSize()
                        else:
                            del(newCopy)

                    #Try to complete the frontier by expanding the tree from this point
                    #First, create all trees that start in the frontier item and ends with obs
                    genSetForObs = PL.generatingSetForObs(deepcopy(allGeneratingSet[node.getRoot().get()]), obs)
                    #Then, try to see if the new sub-tree can be inserted instead of the frontier item
                    for newExpandedTree in genSetForObs:
                        if tree.sameParameters(newExpandedTree.getRoot(), index):
                            newCopy = deepcopy(tree)
                            newCopy.setNodeByFrontierIndex(index, newExpandedTree)
                            if newCopy.substitute(newExpandedTree.getRoot(), index):
                                newExp = deepcopy(currentExp)
                                newExp.setTree(newCopy, treeIndexInExp)
                                newExp.updateLocalProbChoices(newCopy)
                                newExp.resetAge()
                                expsTemp.append(newExp)
                                numOfExps += 1
                                treesTotal += len(newExp.getTrees())
                                probabilityTotal += newExp.getExpProbability()
                                ageTotal += newExp.getAge()
                                frontierTotal += newExp.getFrontierSize()
                            else:
                                del(newCopy)
                treeIndexInExp+=1
                            
            #Consider all the new plans the observation could introduce
            for possTree in goalsGeneratingSet:
                treeFrontier = possTree.getFrontier(withIndices=True)
                for (node, index) in treeFrontier:  
                    if possTree.sameParameters(obs, index):
                        newCopy = deepcopy(possTree)
                        if newCopy.substitute(obs, index):
                                newExp = deepcopy(currentExp)
                                newExp.setTree(newCopy)
                                newExp.backpatchPS(allGeneratingSet[possTree.getRoot().get()])
                                newExp.updateLocalProbChoices(newCopy)
                                newExp.updateLocalProbRoots(PL.getRootProb())
                                newExp.incrementAge()
                                expsTemp.append(newExp)
                                numOfExps += 1
                                treesTotal += len(newExp.getTrees())
                                probabilityTotal += newExp.getExpProbability()
                                ageTotal += newExp.getAge()
                                frontierTotal += newExp.getFrontierSize()
                        else:
                            del(newCopy)
                        
        exps=expsTemp
        TreeAvgBound = treesTotal / numOfExps if 0!=numOfExps else 1000
        AgeAvg = ageTotal / numOfExps if 0!=numOfExps else 1.0
        FrontierAvg = frontierTotal / numOfExps if 0!=numOfExps else 1.0
        
        #Print Measurements:
        #print ProbabilityMin, ",", ProbabilityMax, ",", TreeAmountMin, ",", TreeAmountMax, ",", AgeMin, ",", AgeMax, ",", FrontierMin, ",", FrontierMax
        
        obsNum += 1
    return exps
            