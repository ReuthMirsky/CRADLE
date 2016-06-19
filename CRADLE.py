import sys
import profile
import xml.etree.ElementTree as ET

sys.path.append( "Source" )
from Algorithm import ExplainAndCompute
from Sigma import Sigma, NT
from Rule import Rule
import PL
import Explanation

def readDomainOLD():
    domainFile = open(sys.argv[1])
    domain = domainFile.read()
    SigmasStart = domain.find('Sigmas')+7
    SigmasEnd = domain.find('NTs')
    NTsStart = domain.find('NTs')+4
    NTsEnd = domain.find('Rules')
    RulesStart = domain.find('Rules')+6
    
    #Parse Sigmas
    SigmasString = domain[SigmasStart:SigmasEnd]
    Sigmas = []
    splittedSigmas = SigmasString.strip().split("\n")
    for singleSigma in splittedSigmas:  
        paramIndex = singleSigma.find("[")
        name = singleSigma[:paramIndex].strip(" \n")  
        parameters = singleSigma[paramIndex:]
        splittedParams = eval(parameters.strip())
        sigma = Sigma(name, splittedParams)
        Sigmas.append(sigma)
        
    #Parse NTs
    NTsString = domain[NTsStart:NTsEnd]
    NTs = []
    Goals = []
    splittedNTs = NTsString.strip().split("\n")
    for singleNT in splittedNTs:
        isGoal = False  
        paramIndex = singleNT.find("[")
        name = singleNT[:paramIndex].strip(" \n")
        if name.startswith("*"):
            name = name[-1:]
            isGoal = True              
        parameters = singleNT[paramIndex:]
        splittedParams = eval(parameters.strip())
        nt = NT(name, splittedParams)
        NTs.append(nt)
        if isGoal:
            Goals.append(nt)    
    
    
    #Parse Rules
    Rules = []
    allLetters = Sigmas+NTs
    allRules = domain[RulesStart:].strip().split("#")
    for singleRule in allRules:
        Alpha = []
        delimitedRule = singleRule.split("\n")
        if len(delimitedRule) < 3:
            continue
        #print delimitedRule

        #Retrieve rule's letters 
        leftSide = delimitedRule[1][:delimitedRule[1].index("-")].strip()
        rightSide = delimitedRule[1][delimitedRule[1].index(">")+1:delimitedRule[1].index("[")].strip()
        for constituent in rightSide.split():
            Alpha.append(allLetters[int(constituent)])
        #Retrieve rule's temporal constraints
        temporalConstraints = eval(delimitedRule[1][delimitedRule[1].index("["):].strip())

        #Retrieve rule's parametric constraints
        parametricConstraints = eval(delimitedRule[2].strip())
        
        newRule = Rule(allLetters[int(leftSide)], Alpha, temporalConstraints, parametricConstraints)
        Rules.append(newRule)
        
    return PL.PL(Sigmas, NTs, Goals, Rules)

def readObservationsOLD(domain):
    obsFile = open(sys.argv[2])
    obsString = obsFile.read()
    Observations = []
    for oneObs in obsString.splitlines():
        name =  oneObs[:oneObs.index("[")].strip()
        paramsAsString = oneObs[oneObs.index("["):].strip()
        parameters = eval(paramsAsString)
        newObs = Sigma(name, parameters)
        Observations.append(newObs)
        
    return Observations

#************************************************#

def getLetter(listOfLetters, name):
    for letter in listOfLetters:
        if letter.get()==name:
            return letter
    return None

def readDomain():
    tree = ET.parse(sys.argv[1])
    root = tree.getroot()
    
    #Read NTs
    ntNodes = root[0][0]
    NTs=[]
    Goals=[]
    for child in ntNodes:
        name = child.get('id')
        params = []
        for param in child[0]:
            params.append(param.get('name'))
        newLetter=NT(name, params)
        NTs.append(newLetter)
        if child.get('goal')=='yes':
            Goals.append(newLetter)
        
    #Read Sigmas
    sigmaNodes = root[0][1]
    Sigmas=[]
    for child in sigmaNodes:
        name = child.get('id')
        params = []
        for param in child[0]:
            params.append(param.get('name'))
        Sigmas.append(Sigma(name, params))
    
    
    #Read Rules
    Rules=[]
    ruleNodes = root[1]
    
    for ruleNode in ruleNodes:
        #ruleProb = ruleNode.get('prob')
        ruleA = getLetter(NTs, ruleNode.get('lhs'))
        ruleOrders = []
        ruleEquals = []
        ruleRhs = []
        if ruleNode.find('Order')!=None:
            for orderConst in ruleNode.find('Order'):
                ruleOrders.append((int(orderConst.get('firstIndex'))-1, int(orderConst.get('secondIndex'))-1))
        if ruleNode.find('Equals')!=None:
            for equalConst in ruleNode.find('Equals'):
                ruleEquals.append((int(equalConst.get('firstIndex'))-1, equalConst.get('firstParam'), int(equalConst.get('secondIndex'))-1, equalConst.get('secondParam')))
        for child in ruleNode.findall('Letter'):
            letter = getLetter(NTs, child.get('id'))
            if letter==None:
                letter = getLetter(Sigmas, child.get('id'))
            ruleRhs.insert(int(child.get('index'))-1 , letter)
        Rules.append(Rule(ruleA, ruleRhs, ruleOrders, ruleEquals))
        
    myPL = PL.PL(Sigmas, NTs, Goals, Rules)
    return myPL            
    
def readObservations(pl):
    tree = ET.parse(sys.argv[2])
    root = tree.getroot()
    observations = []
    
    for observation in root:
        letter = getLetter(pl._Sigma, observation.get('id'))
        for param in observation:
            letter.setParam(param.get('name'), param.get('val'))
        observations.append(letter)    
    return observations
    
def main():
        #Usage
    if len(sys.argv) != 3:
        print "Usage: CRADLE.py     <domain file>    <observations file> \n"
        sys.exit()
    try:
        planLibrary = readDomain()
        print planLibrary
    except:
        print "Usage: Domain File Corrupt\n"
        sys.exit()
    
    try:
        observations = readObservations(planLibrary)
    except:
        print "Usage: Observations File Corrupt\n"
        sys.exit()

    profile.runctx('myMain(planLibrary, observations)', globals(), locals())

    
def myMain(planLibrary, observations):

    print planLibrary
    print "Observations:\n", observations
    print "\n-------------------------------------------------------------------------------------\n"    

    exps = ExplainAndCompute(planLibrary, observations)
    
    if len(exps)==0:
        print "No Explnanations"      
    
    explanations = 0
    noFrontier = 0

    exps.sort(key=Explanation.Explanation.getExpProbability)

    firstflag = True
    while not len(exps)==0:
        exp = exps.pop()
        #if firstflag:
        print exp
        firstflag = False
        if exp.getFrontierSize()==0:
            noFrontier += 1
            
        explanations+=1

    print "Explanations: ", explanations
    print "No Frontier Explanations: ", noFrontier
    print "\n-------------------------------------------------------------------------------------\n"    

    sys.exit()   
        

if __name__ == '__main__': main()