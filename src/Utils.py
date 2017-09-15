'''
Created on Mar 24, 2017

@author: Jonathan.Cobb
'''
import os
import sys
import logging

class Utils:
    bat_or_sh = ".bat"
    def __init__(self):
        sys_type = sys.platform
        if "linux" in sys_type:
            self.bat_or_sh = ".sh"
            
    def readFile(self, mydir,filepath):
        fd = open(os.path.join(mydir,filepath),'r')
        content = fd.read()
        fd.close()
        return content

    def writeFile(self, mydir,filepath,content):
        newfile = os.path.join(mydir,filepath)
        fd = open(newfile,'w')
        fd.write(content)
        fd.close()
        return newfile
    
    def readLines(self,mydir,filepath):
        fd = open(os.path.join(mydir,filepath),'r')
        content = fd.read()
        contentlist = content.split('\n')
        return contentlist
    
    def getArgPairs(self, args,separator):
        ret = dict()
        for pairs in args:
            argPair = pairs.split(separator)
            if len(argPair) > 1:
                ret[argPair[0]] = argPair[1]
        return ret

    def tessImg(self,inputfile, outputfile):
        mydir = os.path.dirname(__file__)
        batchf = os.path.join(mydir,'batchfiles/tess'+self.bat_or_sh)
        command = batchf+" "+inputfile+" "+outputfile
        os.system(command)
        outputfile+='.txt'
        fd  = open(outputfile, 'r')
        textstring = fd.read()
        fd.close()
        os.remove(outputfile)
        return textstring
    
    def pdfSplitter(self,inputfile, outputfolder):
        mydir = os.path.dirname(__file__)
        batchf = os.path.join(mydir,'batchfiles/imgMag'+self.bat_or_sh)
        command = batchf+" "+inputfile
        os.system(command)

    def removeSpaceFromFile(self,inputfile):
        mydir = os.path.dirname(__file__)
        batchf = os.path.join(mydir,'batchfiles/Rsf'+self.bat_or_sh)
        command = batchf+" "+inputfile
        os.system(command)
        
    def rotatePdf(self,inputfile, degrees,outputfolder):
        mydir = os.path.dirname(__file__)
        batchf = os.path.join(mydir,'batchfiles/rotate'+self.bat_or_sh)
        command = batchf+" "+inputfile+" "+str(degrees)
        os.system(command)
        
    def logClass(self, name,logpath):
        logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(name)-12s: %(Levelname)-8s %(message)s',
            datefmt = '%m-%d-%y %H:%M',filename=logpath, filemode='w')  
        log = logging.getLogger(name)
        return log
        
    def stjohnsPdf(self,inputfolder):
        mydir = os.path.dirname(__file__)
        batchf = os.path.join(mydir,'batchfiles/stjohns'+self.bat_or_sh)
        command = batchf+" "+str(inputfolder)
        os.system(command)
    
    def searchDoc(self, mydir,filepath, searchitem):
        fd = open(os.path.join(mydir,filepath),'r')
        content = fd.read()
        content = content.replace("\\","/")
        contentlist = content.split('\n')
        myline = ""
        for line in contentlist:
            if searchitem in line:
                myline = line
        fd.close()
        return myline
    
       
    def ccCont(self,inputfile,outputfile):
        mydir = os.path.dirname(__file__)
        batchf = os.path.join(mydir,'batchfiles/ccCont'+self.bat_or_sh)
        command = batchf+' "cc_path='+str(inputfile)+'"'+' "out_path='+str(outputfile)+'"'
        os.system(command)
    
    def createRegexDict(self,mydir,ctfpath,searchitem):
        regexdict = dict()
        mainccfile = self.searchDoc(mydir, ctfpath, searchitem)
        if mainccfile == "":
            return None
        mainccfile = mainccfile.split("<string>")
        mainccfile = mainccfile[1]
        mainccfile = mainccfile.split("</string>")
        mainccfile = mainccfile[0]
        self.ccCont(mainccfile, os.path.join(mydir,"temp.txt"))
        try:
            lines = self.readLines(mydir, "temp.txt")
        except:
            return None
        for line in lines:
            line_split = line.split('@')
            if line != "":
                regexdict[line_split[0]]=line_split[1]
        os.remove(os.path.join(mydir,"temp.txt"))
        return regexdict
    
    def ccCreator(self,outputfolder,split_key_,county,validLine_reg,cert_reg,block_reg,lot_reg,qual_reg,
                  parcel_reg,lien_year_reg,tax_year_reg,total_reg,multiline):
        mydir = os.path.dirname(__file__)
        command = self.readFile(mydir, 'batchfiles/ccCreator'+self.bat_or_sh)
        newccpath='"newccpath='+outputfolder+'"'
        split_key='"split_key='+split_key_+'"'
        countyName='"county='+county+'"'
        validLine='"validLine='+validLine_reg+'"'
        cert='"cert='+cert_reg+'"'
        parcel='"parcel='+parcel_reg+'"'
        lien_year='"lien_year='+lien_year_reg+'"'
        block='"block='+block_reg+'"'
        lot='"lot='+lot_reg+'"'
        qual='"qual='+qual_reg+'"'
        tax_year='"tax_year='+tax_year_reg+'"'
        total='"total='+total_reg+'"'
        mult='"multiline='+multiline+'"'
        command += ' '+newccpath+' '+split_key+' '+countyName+' '+block+' '+' '+lot+' '+qual+' '+\
        validLine+' '+cert+' '+parcel+' '+lien_year+' '+tax_year+' '+total+' '+mult
        self.writeFile(mydir, "temp"+self.bat_or_sh, command)
        os.system("temp"+self.bat_or_sh)
        
    def addCcToCtf(self,cc_path,ctf_path):
        mydir = os.path.dirname(__file__)
        batchf = os.path.join(mydir,'batchfiles/addCcToCtf'+self.bat_or_sh)
        ctfXmlFilePath='"ctfXmlFilePath='+ctf_path+'"'
        ccXmlFilePath='"ccXmlFilePath='+cc_path+'"'
        command = batchf+" "+ctfXmlFilePath+" "+ccXmlFilePath
        os.system(command)