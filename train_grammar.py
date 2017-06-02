import sys
import tree
import csv

def exploreTree(root):
    if len(root.children) == 1:
        pos = str(root)
        word = str(root.children[0])
        entry = (pos, word)
        if pos in poses.keys(): poses[pos] += 1
        else: poses[pos] = 1
        if word in words.keys(): words[word] += 1
        else: words[word] = 1
        if entry in unary.keys(): unary[entry] += 1
        else: unary[entry] = 1
    if len(root.children) != 2 :
        return
    kids = []
    for child in root.children:
        kids.append(str(child))
    pos = str(root)
    entry = (pos ,kids[0], kids[1])
    if pos in poses.keys(): poses[pos] += 1
    else: poses[pos] = 1
    if entry in binary.keys(): binary[entry] += 1
    else: binary[entry] = 1
    exploreTree(root.children[0])
    exploreTree(root.children[1])

def printState():
    unary_ordered = sorted(unary, key=unary.get, reverse=True)
    binary_ordered = sorted(binary, key=binary.get, reverse=True)
    for (top,kid1,kid2) in binary_ordered:
        print(top,'->(',kid1,',',kid2,')=',binary[(top,kid1,kid2)],';',P_binary[(top,kid1,kid2)])
    for (item,word) in unary_ordered:
        print(item,'->',word,'=',unary[(item,word)],';',P_unary[(item,word)])

def mostFreqTrans():
    # merge transition probabilities
    transitions = unary.copy()
    transitions.update(binary)
    p_trans = P_unary.copy()
    p_trans.update(P_binary)
    # list the ten most frequent rules in training and their frequencies
    best_trans = sorted(transitions, key=transitions.get, reverse=True)[:10]
    for trans in best_trans:
        print(trans[0],'->',str(trans[1:]),'=',transitions[trans],';',p_trans[trans])

if __name__ == "__main__":
    if len(sys.argv) == 2:
        _, trainFile, grammarFile = sys.argv
    else:
        print("usage: python train_grammar.py train.trees grammar.csv")
        print("<Using Default Parameters>\n...")
        trainFile = "train.trees"
        grammarFile = "grammar.csv"

    train = open(trainFile, 'r')
    grammar = open(grammarFile, 'w')


    # Important Variables
    poses = {} # pos[tag] = count
    words = {} # words[word] = count
    unary = {}  # unary[(DT, the)] = count; Laplace smoothed
    binary = {} # binary[(from,into,into)] = count; Not smoothed
    P_unary = {}
    P_binary = {}

    # Read training file
    for line in train:
        sentenceTree = tree.Tree.from_str(line)
        root = sentenceTree.root
        exploreTree(root)

    # generate the Laplace probabilities for unary rules
    for word in words.keys():
        for pos in poses.keys():
            if (pos, word) not in unary.keys():
                Laplace = 1 / (poses[pos] + len(unary) + 1)
                unary[(pos,word)] = 0
                P_unary[(pos,word)] = Laplace
                continue
            else:
                count = unary[(pos,word)]
                Laplace = (count + 1)
                Laplace /= (poses[pos] + len(unary) + 1)
                P_unary[(pos, word)] = Laplace

    # generate the MLE probabilities for the binary rules
    for (start, into1, into2), count in binary.items():
        startCount = 0
        for (s, in1, in2), c in binary.items():
            if start == s:
                startCount += binary[(s, in1, in2)]
        MLE = count / startCount
        P_binary[(start, into1, into2)] = MLE

    # write out grammar to file
    grammar = open(grammarFile, 'w')
    for (item,word), count in unary.items():
        prob = P_unary[(item,word)]
        count = str(count)
        prob = str(prob)
        grammar.write(item + '\t' + word + '\t' + count + '\t' + prob + '\n')
    for (top,kid1,kid2), count in binary.items():
        prob = P_binary[(top,kid1,kid2)]
        count = str(count)
        prob = str(prob)
        grammar.write(top + '\t' + kid1 + '\t' + kid2 + '\t' + count + '\t' + prob + '\n')

    # print stats
    print(len(P_unary), "unary rules")
    print(len(P_binary), "binary rules")
    #mostFreqTrans()
    #printState()
