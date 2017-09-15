import random
from Utils import Utils
import os
import sys
mydir = os.path.dirname(__file__)

util = Utils()

def knapsack(addem,curlist,seek):
    total = 0
    for i in addem:
        curlist.append(i)
        total+=float(i)
        if total == seek:
            print str(total)+ ' == '+ str(seek) +'\nList: '+str(curlist)
            return True
        elif total > seek:
            return False

def stjohnsdict(inputfolder,seeklist):
    content = util.readLines(mydir, "stjohns.txt")
    totdict = dict()
    addem = list()
    fwcontent = str()
    for line in content:
        if "@" in line:
            line_split = line.split("@")
            totdict[line_split[0]] = line_split[1]
            addem.append(line_split[0])
    curlist = list()
    random.shuffle(addem)
    
    for seek in seeklist:
        curlist = []
        statustot = False
        statustot = knapsack(addem,curlist,seek)
        
        while statustot == False:
            curlist = []
            random.shuffle(addem)
            statustot = knapsack(addem,curlist,seek)
        
        for tot in curlist:
            if tot in addem:
                addem.remove(tot)
        
        fwcontent = ""
        for line in curlist:
            fwcontent += totdict.get(line) + "\n"
        filepath = "stjohns"+str(seek)+".txt"
        util.writeFile(mydir, filepath, fwcontent)
        fwcontent = ""
        for line in addem:
            fwcontent += line + "@" +totdict.get(line) + "\n"
        filepath = "Stjohns.txt"
#         print fwcontent
        util.writeFile(mydir, filepath, fwcontent)
    return addem


other = [1367.52,22429.30,13194.75]
argsm = sys.argv[1:]
argMap = Utils().getArgPairs(argsm, "=")
inputfolder = argMap.get('folder')
util.stjohnsPdf(inputfolder)
addem_sum = util.readLines(mydir, "stjohns.txt")
sum_em_up = 0
for line in addem_sum:
        if "@" in line:
            line_split = line.split("@")
            sum_em_up += float(line_split[0])

othersum = 0
print str(sum_em_up) + " - "+str(othersum)+" = "+str(sum_em_up-othersum) 


remaining = stjohnsdict(inputfolder, other) 
print remaining

#[1639.21, 1121.28, 1426.2, 900.38, 1340.41, 1695.37, 9081.12, 7344.09, 630.75, 2893.97, 3265.89, 312.53]