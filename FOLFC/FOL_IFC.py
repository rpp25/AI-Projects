import re
import copy
import sys

rules = []
facts = []
inferred = []
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
                # print(str(atoms))
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
        return None, True
    else:
        #print("Same predicate: " + atom.name)
        good = True
        for i in range(0, len(atom.args)):
            if(isVariable(atom.args[i])):
                if(atom.args[i] in subs):
                    if (atom.args[i] == fact.args[i]):
                        good = False
                        continue
                    else:
                        # good = False
                        continue
                    # return None, True
                else:
                    subs[atom.args[i]] = fact.args[i]
    # print(str(subs))

    return subs, good

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

def atomEquals(atom1, atom2):
    yes = True
    if atom1.name != atom2.name or atom1.args != atom2.args:
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
        # print(str(x.args))
        if fact.name == x.name and fact.args == x.args:
            # print("yes")
            yes = True

    return yes

def recurse(rule, facts, index):

    if index == len(facts):
        # print(rule.toString())
        return [rule]

    newlyInferred = []
    for i in range(index, len(facts)):
        origRule = copy.deepcopy(rule)
        newRule = apply(facts[i], rule)
        # print("NEW RULE: " + newRule.toString())
        # if rule got updated, if not move on to next fact
        if not isEqual(newRule,origRule):
            newlyInferred.append(newRule)
            newRules = recurse(newRule, facts, i+1)
            for x in newRules:
                if not isEqual(x,origRule):
                    newlyInferred.append(x)

    return newlyInferred

def apply(fact, rule):
    for atom in rule.lhs:
        if atom.name == fact.name:
            currAtom = copy.deepcopy(atom)
            subbed = True
            #is a fact
            for arg in atom.args:
                if isVariable(arg):
                    subbed = False
            #if so, skip this atom

            if subbed == True:
                continue
            subs, good = unify(atom, fact, rule.subs)
            # print(subs)
            if subs is not None:
                changed = True
                if good:
                    invalid = False
                    for i in range(0, len(fact.args)):
                        # if current atom arg is a variable and if that
                        if isVariable(atom.args[i]) and subs[atom.args[i]] == fact.args[i]:
                            rule.lhs[rule.lhs.index(atom)].args[i] = fact.args[i]
                        else:
                            invalid = True
                    if invalid == True:
                        rule.lhs[rule.lhs.index(atom)].args = currAtom.args
    return rule

def folifc(rules, facts, goal):
    count = 1
    new = []
    # newFacts = facts
    # newRules = []
    while len(facts) > 0:
        while len(rules) > 0:
            rule = rules.pop(0)
            changed = False
            print("\n")
            print("Iteration: " + str(count))

            # print(rule.toString() + " POPPED")
            toSub = True
            # newRule = copy.deepcopy(rule)
            newRule2 = None

            # for fact in facts:
            #     print(fact.name+str(fact.args))
            currRule = copy.deepcopy(rule)
            print("\n")
            new = recurse(currRule, facts, 0)

            if len(new) > 0:
                newRule = new[-1]
                # check if LHS contains all facts; if there is one variable, fails
                isFact = True
                for x in newRule.lhs:
                    for y in x.args:
                        if isVariable(y):
                            isFact = False

                subs = newRule.subs
                if isFact == True:
                    for x in newRule.rhs.args:
                        if x in subs:
                            newRule.rhs.args[newRule.rhs.args.index(x)] = subs[x]
                    newFact = newRule.rhs

                    # print(newFact.name+str(newFact.args))
                    # print(factIsIn(newFact,inferred))
                    if not factIsIn(newFact,facts) and not factIsIn(newFact,inferred):
                        facts.append(newFact)
                        inferred.append(newFact)
                        statements.append(newRule)


                    if newFact.name == goal.name and newFact.args == goal.args:
                        allUnified = True

                        for c in newRule.lhs:
                            for b in c.args:
                                if b not in list(subs.values()):
                                    allUnified = False

                        if allUnified == True:
                            return True, statements, subs

                else:
                    rules.append(newRule)



            count = count + 1

        for f in inferred:
            print(f.name+str(f.args))

        for fact in facts:
            facts.remove(fact)
        facts.extend(inferred)
        del inferred[:]

    return False, statements, None

if __name__ == '__main__':
    if len(sys.argv) == 2:
        setup(sys.argv[1])
        goal = facts[-1]
        facts.remove(goal)

        result, infer, finalSubs = folifc(rules, facts, goal)

        # f = open('helloworld.txt','w')
        # f.write('hello world')
        # f.close()
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
