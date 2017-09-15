'''
Created on Apr 19, 2017

@author: Jonathan.Cobb
'''
import os
import sys
from Utils import Utils

class CreatePids:
    util = None
    bat_or_sh = ".bat"
    
    def __init__(self):
        self.util = Utils() 
        sys_type = sys.platform
        if "linux" in sys_type:
            self.bat_or_sh = ".sh"
    
    def CreatePids(self,url,uid,password,db,rocrvsqlpath,dfn_or_syscounty,countytxtpath):
        mydir = os.path.dirname(__file__)
        batchf = os.path.join(mydir,'batchfiles/createpid'+self.bat_or_sh)
        param1 = "url@"+url
        param2 = "uid@"+uid
        param3 = "password@"+password
        param4 = "databaseName@"+db
        sqlfile = self.util.writeFile(mydir, 'sqlFiles/Docv/temp.sql', rocrvsqlpath)
        param5 = "rocrvSqlFile@"+sqlfile
        param6 = "countyTxtFilesXmlPath@"+countytxtpath
        param7 = "dfn_or_syscounty@"+dfn_or_syscounty
        command = batchf+' "'+param1+'" "'+param2+'" "'+param3+'" "'+param4+\
        '" "'+param5+'" "'+param6+'"'+' "'+param7+'"'
        os.system(command)
        
    def CreatePidsOverride(self,url,uid,password,db,rocrvsqlpath,dfn_or_syscounty,countytxtpath):
        mydir = os.path.dirname(__file__)
        batchf = os.path.join(mydir,'batchfiles/createpid'+self.bat_or_sh)
        param1 = "url@"+url
        param2 = "uid@"+uid
        param3 = "password@"+password
        param4 = "databaseName@"+db
        sqlfile = self.util.writeFile(mydir, 'sqlFiles/Docv/temp.sql', rocrvsqlpath)
        param5 = "rocrvSqlFile@"+sqlfile
        param6 = "countyTxtFilesXmlPath@"+countytxtpath
        param7 = "dfn_or_syscounty@"+dfn_or_syscounty
        param8 = "override@true"
        command = batchf+' "'+param1+'" "'+param2+'" "'+param3+'" "'+param4+\
        '" "'+param5+'" "'+param6+'" "'+param7+'" '+'"'+param8+'"'
        os.system(command)
        
        
class CreateDocv:
    util = None 
    bat_or_sh = None
    
    def __init__(self):
        self.util = Utils() 
        self.bat_or_sh = self.util.bat_or_sh
           
    def Docv(self,url,uid,password,db,rocrvsqlpath):
        mydir = os.path.dirname(__file__)
        batchf = os.path.join(mydir,'batchfiles/Docv'+self.bat_or_sh)
        param1 = "url@"+url
        param2 = "uid@"+uid
        param3 = "password@"+password
        param4 = "databaseName@"+db
        sqlfile = self.util.writeFile(mydir, 'sqlFiles/Docv/temp.sql', rocrvsqlpath)
        param5 = "rocrvSqlFile@"+sqlfile
        command = batchf+' "'+param1+'" "'+param2+'" "'+\
        param3+'" "'+param4+'" "'+param5+'" "'
        os.system(command)
        
    def DocvCo(self,url,uid,password,db,rocrvsqlpath):
        mydir = os.path.dirname(__file__)
        batchf = os.path.join(mydir,'batchfiles/DocvCO'+self.bat_or_sh)
        param1 = "url@"+url
        param2 = "uid@"+uid
        param3 = "password@"+password
        param4 = "databaseName@"+db
        sqlfile = self.util.writeFile(mydir, 'sqlFiles/Docv/temp.sql', rocrvsqlpath)
        param5 = "rocrvSqlFile@"+sqlfile
        command = batchf+' "'+param1+'" "'+param2+'" "'+\
        param3+'" "'+param4+'" "'+param5+'" "'
        os.system(command)
        
    def InsertOcr(self,url,uid,password,db,pdfpath,depid):
        mydir = os.path.dirname(__file__)
        batchf = os.path.join(mydir,'batchfiles/InsertOcr'+self.bat_or_sh)
        param1 = "url="+url
        param2 = "uid="+uid
        param3 = "password="+password
        param4 = "databaseName="+db
        param5 = "pdfpath="+pdfpath
        param6 = "depid="+str(depid)
        command = batchf+' "'+param1+'" "'+param2+'" "'+\
        param3+'" "'+param4+'" "'+param5+'" "'+param6+'"'
        os.system(command)