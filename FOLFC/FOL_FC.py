import re
import copy
import sys

rules = []
facts = []
inferred = []
infRules = []
statements = []

class Atom:
    def __init__(self, name, args):
        self.name = name
        self.args = args

class Rule:
    def __init__(self):
        self.lhs = []
        self.rhs = None
        self.subs = dict()

    def toString(self):
        templhs = [(w.name, w.args) for w in self.lhs]

        if (self.rhs != None):
            return("LHS: " + str(templhs) + ", RHS: " + self.rhs.name + " " + str(self.rhs.args))
        else:
            return("LHS: " + str(templhs))

def setup(inputFile):
    with open(inputFile, 'r+') as f:
        for line in f:
            list = re.findall('[\w,()]+', line)
            newRule = Rule()
            if ('PROVE' in list):
                list.remove('PROVE')
            if (len(list)> 1):
                temp = list[:-1]
                # print(temp)
                atoms = []
                for x in temp:
                    tempName = re.match('^[^\(]+', x)
                    tempArgs = re.search('\(.*?\)', x)
                    newAtom = Atom(tempName.group(0), tempArgs.group(0).strip('() ').split(','))
                    atoms.append(newAtom)
                newRule.lhs = atoms
                newRHS = list[-1]
                rhsName = re.match('^[^\(]+', newRHS)
                rhsArgs = re.search('\(.*?\)', newRHS)
                rhsAtom = Atom(rhsName.group(0), rhsArgs.group(0).strip('() ').split(','))
                newRule.rhs = rhsAtom
                rules.append(newRule)
            else:
                rule = list[0]
                tempName = re.match('^[^\(]+', rule)
                tempArgs = re.search('\(.*?\)', rule)
                newAtom = Atom(tempName.group(0), tempArgs.group(0).strip('() ').split(','))
                facts.append(newAtom)
    f.close()

def unify(atom, fact, subs):
    if(atom.name != fact.name or len(atom.args) != len(fact.args)):
        # print("Yea")
        return None
    else:
        #print("Same predicate: " + atom.name)
        for i in range(0, len(atom.args)):
            if(isVariable(atom.args[i])):
                if(atom.args[i] in subs):
                    continue
                else:
                    subs[atom.args[i]] = fact.args[i]
    # print(str(subs))

    return subs

def isVariable(x):
    return x.islower()

# if rule1 is equivalent to rule2
def isEqual(x, y):
    yes = True
    if (len(x.lhs) != len(y.lhs)):
        yes = False
    else:
        # for each atom in x
        for i in range(0, len(x.lhs)):
            # if the atoms don't have the same name, or the args don't match, false
            if x.lhs[i].name != y.lhs[i].name or x.lhs[i].args != y.lhs[i].args:
                yes = False

    return yes

# if rule is in the knowledge base
def isIn(rule, rules):
    yes = False
    for x in rules:
        if isEqual(x, rule):
            yes = True

    return yes

#if fact is in facts
def factIsIn(fact, facts):
    yes = False
    for x in facts:
        if fact.name == x.name and fact.args == x.args:
            yes = True

    return yes

def folfc(rules, facts, goal):
    count = 1
    while len(rules) > 0:
        rule = rules.pop(0)
        changed = False
        for atom in rule.lhs:
            subbed = True
            for arg in atom.args:
                if isVariable(arg):
                    subbed = False
            if subbed == True:
                continue

            for fact in facts:
                #the fact's name matches the current atom's name
                if atom.name == fact.name:
                    newRule = copy.deepcopy(rule)
                    subs = unify(atom, fact, newRule.subs)
                    invalid = False
                    for i in range(0, len(fact.args)):
                        if isVariable(newRule.lhs[rule.lhs.index(atom)].args[i]) and subs[newRule.lhs[rule.lhs.index(atom)].args[i]] == fact.args[i]:
                                newRule.lhs[rule.lhs.index(atom)].args[i] = fact.args[i]
                        else:
                            invalid = True

                    changed = True

                    # check if LHS contains all facts; if there is one variable, fails
                    isFact = True
                    for x in newRule.lhs:
                        for y in x.args:
                            if isVariable(y):
                                isFact = False

                    # print(str(subs))
                    if isFact == True:
                        for x in newRule.rhs.args:
                            if x in subs:
                                newRule.rhs.args[newRule.rhs.args.index(x)] = subs[x]
                        newFact = newRule.rhs


                        if not factIsIn(newFact,facts) and not factIsIn(newFact,inferred):
                            facts.append(newFact)
                            inferred.append(newFact)
                            statements.append(newRule)
                            same = True
                            checkArg = newFact.args[0]
                            for x in newFact.args:
                                if x != checkArg:
                                    same = False


                        if newFact.name == goal.name and newFact.args == goal.args:
                            allUnified = True

                            for c in newRule.lhs:
                                for b in c.args:
                                    if b not in list(subs.values()):
                                        allUnified = False

                            if allUnified == True:
                                return True, statements, subs
                    if not isIn(newRule, rules) and isFact == False and invalid == False:
                        rules.append(newRule)
                        infRules.append(newRule)

        if changed == False:
            rules.append(rule)
        count = count + 1

    return False, statements, None

if __name__ == '__main__':
    if len(sys.argv) == 2:
        setup(sys.argv[1])
        goal = facts[-1]
        facts.remove(goal)

        result, infer, finalSubs = folfc(rules, facts, goal)

        fname = str(sys.argv[1]).strip('.txt') + '_out_FC.txt'
        # print(fname)
        f = open(fname,'w')
        f.write("FINAL RESULT: " + str(result) + "\n")
        f.write("Rules inferred: " + "\n")
        for x in infRules:
            f.write(str(infRules.index(x)+1)+"\t"+x.toString()+"\n")
        f.write("Facts inferred (includes the rules generated that implies the fact): " + "\n")
        for i in range(0,len(infer)):
            if i != (len(infer) - 1):
                f.write("\t" + infer[i].toString() + "\n")
            else:
                if result:
                    f.write("\tFinal Conclusion: " + infer[i].toString() + "\n")
                else:
                    f.write("\t" + infer[i].toString() + "\n")
        f.close()

        print("FINAL RESULT: " + str(result))
        print("Facts inferred: ")
        for i in range(0,len(infer)):
            if i != (len(infer) - 1):
                print("\t" + infer[i].toString())
            else:
                if result:
                    print("\tFinal Conclusion: " + infer[i].toString())
                else:
                    print("\t" + infer[i].toString())
