import sys
import itertools, collections
import tree
import string

if len(sys.argv) == 3:
    _, parsefilename, goldfilename = sys.argv
else:
    sys.stderr.write("<default parameters> usage: evalb.py <parse-file> <gold-file>\n\n")
    parsefilename = 'output.trees'
    goldfilename = 'test.trees'

def _brackets_helper(node, i, result):
    i_0 = i
    if len(node.children) > 0:
        for child in node.children:
            i = _brackets_helper(child, i, result)
        j0 = i
        if len(node.children[0].children) > 0: # don't count preterminals
            result[node.label, i_0, j0] += 1
    else:
        j0 = i_0 + 1
    return j0

def brackets(t):
    result = collections.defaultdict(int)
    _brackets_helper(t.root, 0, result)
    return result

# --- PROGRAM STARTS HERE --- #

matchcount = parsecount = goldcount = 0

for parseline, goldline in zip(open(parsefilename), open(goldfilename)):
    gold = tree.Tree.from_str(goldline)
    goldbrackets = brackets(gold)
    goldcount += len(goldbrackets)

    if parseline.strip() == "0":
        continue

    parse = tree.Tree.from_str(parseline)
    parsebrackets = brackets(parse)
    parsecount += len(parsebrackets)

    for bracket,count in parsebrackets.items():
        matchcount += min(count,goldbrackets[bracket])

# Calculate stats
if parsecount == 0: precision = 0.0
else: precision = float(matchcount) / parsecount
if goldcount == 0: recall = 0.0
else: recall = float(matchcount) / goldcount
if matchcount == 0: F1 = 0.0
else: F1 = (2.0 / (goldcount / float(matchcount) + parsecount / float(matchcount)))

print(parsefilename,'\t',parsecount,'brackets') #"%s\t%d brackets" % (parsefilename, parsecount)
print(goldfilename,'\t',goldcount,'brackets') #"%s\t%d brackets" % (goldfilename, goldcount)
print('matching\t',matchcount,'brackets') #"matching\t%d brackets" % matchcount
print("Precision\t",precision)
print("Recall\t\t", recall)
print("F1\t\t", F1)
