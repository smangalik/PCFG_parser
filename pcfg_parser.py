import sys
import tree
import csv
import copy

class Cell:
    score = []
    to = []
    fro = []
    def __init__(self, score, fro, to):
        self.score = score
        self.to = to
        self.fro = fro
    def __str__(self):
        return str(self.to)+str(self.fro)+str(self.score)
    def toAdd(self, x):
        self.to.append(x)
    def toSet(self, index, x):
        self.to[index] = x
    def froAdd(self, x):
        self.fro.append(x)
    def scoreAdd(self, x):
        self.score.append(x)
    def scoreSet(self, index, x):
        self.score[index] = x

def cykParse():
    for i in reversed(range(len(words))):
        for j in range(len(words)):
            #  retain the best parse at each cell for each constituent type
            if i == j: # diagonal
                entry = Cell([],[],[])
                for (pos, word), prob in P_unary.items():
                    if word == words[i]:
                        child = tree.Node(words[i],[])
                        parent = tree.Node(pos,[child])
                        #print(tree.Tree(parent), prob)
                        entry.toAdd(parent)
                        entry.froAdd(pos)
                        entry.scoreAdd(prob)
                cells[i][j] = entry
            elif j > i: # valid non-diagonal
                # join cells
                entry = Cell([],[],[])
                for c in range(i,j):
                    cell1 = cells[i][c]
                    cell2 = cells[c+1][j]
                    if cell1.fro != [] and cell2.fro != []:
                        binaryHits(cell1, cell2, entry)
                cells[i][j] = entry
            else: # invalid non-diagonal
                continue

def binaryHits(cell1, cell2, entry):
    for x in range(len(cell1.fro)):
        for y in range(len(cell2.fro)):
            for (start, into1, into2), prob in P_binary.items():
                if cell1.fro[x] == into1 and cell2.fro[y] == into2:
                    join_score = cell1.score[x] * cell2.score[y] * prob
                    c2String = str(tree.Tree(cell2.to[y]))
                    child2 = tree.Tree.from_str(c2String).root
                    c1String = str(tree.Tree(cell1.to[x]))
                    child1 = tree.Tree.from_str(c1String).root
                    parent = tree.Node(start, [child1,child2])
                    if start not in entry.fro:
                        entry.toAdd(parent)
                        entry.froAdd(start)
                        entry.scoreAdd(join_score)
                    else: # clean redundancies
                        cIndex = entry.fro.index(start)
                        if join_score > entry.score[cIndex]:
                            entry.toSet(cIndex, parent)
                            entry.scoreSet(cIndex, join_score)

if __name__ == "__main__":
    if len(sys.argv) == 2:
        _, grammarFile, testFile, outputFile = sys.argv
    else:
        print("usage: python pcfg_parser.py grammar.csv test.txt output.trees")
        print("<Using Default Parameters>\n...")
        grammarFile = "grammar.csv"
        testFile = "test.txt"
        outputFile = "output.trees"

    grammar = open(grammarFile, 'r')
    test = open(testFile, 'r')
    output = open(outputFile, 'w')

    # Important Variables
    unary = {}  # unary[(DT, the)] = count; Laplace smoothed
    binary = {} # binary[(from,into,into)] = count; Not smoothed
    P_unary = {}
    P_binary = {}
    P_unary_big = {}

    # Read grammar file
    with grammar as csvfile:
        csvreader = csv.reader(csvfile, delimiter='\t', quotechar='|')
        for row in csvreader:
            if len(row) == 4:
                item, word, count, prob = row
                count = int(count)
                prob = float(prob)
                unary[(item, word)] = count
                P_unary_big[(item, word)] = prob
                if count != 0:
                    P_unary[(item, word)] = prob
            if len(row) == 5:
                top, kid1, kid2, count, prob = row
                binary[(top, kid1, kid2)] = int(count)
                P_binary[(top, kid1, kid2)] = float(prob)

    # CYK Parser
    for line in test:
        words = line.split()
        arrayLength = len(words)
        cells = [[None for y in range(len(words))] for x in range(len(words))]

        cykParse()

        # Output best parses
        lastCell = cells[0][len(words)-1]
        bestIndex = -1
        bestScore = float('-inf')
        for n in range(len(lastCell.fro)):
            if lastCell.fro[n] == 'TOP':
                if lastCell.score[n] > bestScore:
                    bestScore = lastCell.score[n]
                    bestIndex = n
        if bestIndex > -1:
            lastNode = lastCell.to[bestIndex]
            final_output = str(tree.Tree(lastNode)).replace("\"","")
            output.write(final_output + "\n")
            print('>',final_output, lastCell.score[bestIndex])
        else:
            # retry with big list
            Dup_unary = copy.copy(P_unary)
            P_unary = P_unary_big
            cykParse()
            P_unary = Dup_unary

            lastCell = cells[0][len(words)-1]
            bestIndex = -1
            bestScore = float('-inf')
            for n in range(len(lastCell.fro)):
                if lastCell.fro[n] == 'TOP':
                    if lastCell.score[n] > bestScore:
                        bestScore = lastCell.score[n]
                        bestIndex = n

            lastNode = lastCell.to[bestIndex]
            final_output = str(tree.Tree(lastNode)).replace("\"","")
            output.write(final_output + "\n")
            print('>',final_output, lastCell.score[bestIndex])

        #exit()
