'''
Created on Mar 24, 2017

@author: Jonathan.Cobb
'''
import psycopg2

class Sql:
    pgconnect = None 
    log = None
    
    
    def __init__(self,hostname,username, password,db):
        try:
            self.pgconnect = psycopg2.connect(host = hostname , user=username,password=password, dbname=db)
        except:
            print('Problems connecting to db')
    
    def find(self,query):
        cur = self.pgconnect.cursor()
        try:
            cur.execute(query)
        except:
            print('Issue with your query: '+query)
            return None
        
        rows = cur.fetchall()
        return rows
    
    def findOne(self,query):
        cur = self.pgconnect.cursor()
        try:
            cur.execute(query)
        except:
            print('Issue with your query: '+query)
            return None
        
        rows = cur.fetchone()
        return rows
    
    def tableInfo(self,query):
        cur = self.pgconnect.cursor()
        
        try:
            cur.execute(query)
            col = list()
            col = cur.description
        except:
            print("Error issue with query: "+query)
            return None
        
        return col
    
    def colNames(self,query):
        col = list()
        try:
            info = self.tableInfo(query)
            for column in info:
                col.append(column[0]) 
        except:
            print("Error issue with query: "+query)
            return None
        
        return col
    
    def insert(self,table,values):
        cur = self.pgconnect.cursor()
        query = "select * from "+table+" limit 1;"
        col = self.colNames(query)
        if col is None:
            print(table+" doesn't exist")
            return
        colString = str()
        for acol in col:
            if acol == 'id':
                continue
            colString += str(acol)+","
        colString = colString[:-1]
        valString = str()
        for value in values:
            if value is None or value == '':
                value = "Null"
            valString += str(value)+","
        valString = valString[:-1]
        query = "Insert into "+table+" ("+colString+\
        ") values ("+valString+");"
        try:
            cur.execute(query)
            self.pgconnect.commit()
        except:
            print("Issue with your insert statement: "+query)
        
    def update(self, table, up_col,values,keycol,keyval):
        cur = self.pgconnect.cursor()
        query = "select * from "+table+" limit 1;"
        col = self.colNames(query)
        if col is None:
            print(table+" doesn't exist")
            return
        elif len(up_col) != len(values):
            print('Each column needs an associated value')
            return
        elif len(up_col) == 0:
            print("No columns supplied")
            return
        colString = ''
        for i in range(len(up_col)):
            values[i] = 'Null' if values[i] == 'None' else values[i]
            colString += up_col[i]+'='+values[i]+','
        colString = colString[:-1]
        valString = str()
        for value in values:
            if value is None or value == '':
                value = "Null"
            valString += value+","
        valString = valString[:-1]
        query = "Update "+table+" set "+colString+" where "+keycol+" = "+keyval
        try:
            cur.execute(query)
            self.pgconnect.commit()
        except:
            print("Issue with your update statement: "+query)
            
    def delete(self,table, keycol,keyval):
        cur = self.pgconnect.cursor()
        query = "select * from "+table+" limit 1;"
        col = self.colNames(query)
        if col is None:
            print(table+" doesn't exist")
            return
        query = "delete from "+table+" where "+keycol+" = "+keyval
        try:
            cur.execute(query)
            self.pgconnect.commit()
        except:
            print("Issue with your delete statement: "+query)