'''
Created on Mar 24, 2017

@author: Jonathan.Cobb
'''
import os
from flask import Flask
from datetime import datetime, timedelta
from Sql import Sql
import pandas as pd
from Utils import Utils
from flask.templating import render_template
import sys

app = Flask(__name__)



@app.route('/')
@app.route("/pracfile/<results>")
def pracfile(results=None):
    #Get sql
    mydir = os.path.dirname(__file__)
    util = Utils()
    content = util.readFile(mydir,'sqlFiles/pracquery.sql')
    date = datetime.today()- timedelta(days=3)
    query = content.replace('(REPLACE DATE)', str(date))
    # Get args from run config
    args = sys.argv[1:]
    argMap = util.getArgPairs(args, "=")
    url = argMap.get("url")
    uid = argMap.get("uid")
    password = argMap.get("password")
    db = argMap.get("db")
    
    #get data returned by query
    sql = Sql(url,uid,password,db)
    row = sql.find(query)
    col = sql.colNames(query)
    rows = pd.DataFrame(row, columns=col)
    if rows is None:
        return '<h1>No Data returned<h1>'
    ids = rows['old_fig_deposits_record_id']
    df2 = rows[rows.old_fig_deposits_record_id==20564].to_html(classes='',index=False,border=0).replace('dataframe','pidrec')
    df_results = rows.to_html(classes='',index=False,border=0).replace('dataframe','pidrec')
    #render html
    return render_template('parcel_input.html',results = df_results, idlist=ids, df2=df2)


if __name__=="__main__":
    app.run(debug=True)