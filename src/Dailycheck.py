'''
Created on Mar 24, 2017

@author: Jonathan.Cobb
'''
import os
from flask import Flask, render_template, request,make_response, url_for
from Sql import Sql
import pandas as pd
from Utils import Utils
import sys
from autoRedeem import CreatePids, CreateDocv
import qbapi.qbapi as qb
from werkzeug import redirect

app = Flask(__name__,template_folder='templates')
mydir = os.getcwd()
app.secret_key = Utils().readFile(mydir, 'secret_key.txt')


def createDictFromArgs():
    argsm = sys.argv[1:]
    argMap = Utils().getArgPairs(argsm, "=")
    url = argMap.get("url")
    uid = argMap.get("uid")
    password = argMap.get("password")
    db = argMap.get("db")
    myport = argMap.get("port")
    
    argDict = {'url':url,'uid':uid,'pass':password,'db':db,'dir':mydir,"port":myport}
    return argDict

def createDfFromSql(query,url,uid,password,db):
    row = sql.find(query)
    col = sql.colNames(query)
    row = pd.DataFrame(row, columns=col)
    if len(row) > 0: 
        return row.to_html(classes='',index=False,border=0,na_rep='')
    else:
        return None

def createDfFromSql2(query,url,uid,password,db):
    row = sql.find(query)
    col = sql.colNames(query)
    row = pd.DataFrame(row, columns=col)
    return row.to_dict()

def createDfFromSql1(query,url,uid,password,db):
    row = sql.find(query)
    col = sql.colNames(query)
    row = pd.DataFrame(row, columns=col)
    return row

def replaceCounty(content,county):
    query = content.replace('/*', '')
    query = query.replace('*/', '')
    query = query.replace('(DFN OR COUNTY)', 'syscountyname')
    return query.replace('(REPLACE COUNTY)',county)

def replaceDfn(content,county):
    query = content.replace('/*', '')
    query = query.replace('*/', '')
    query = query.replace('(DFN OR COUNTY)', 'district_full_name')
    return query.replace('(REPLACE COUNTY)',county)


def getCountyDict():
    fields = "8"
    token ='cxeyvydbvik5y3523fepbiue8q2'
    tid = 'bk2q3thup'
    qstringofrqb="{36.GT.'1'}"
    row = qb.query_table(token,tid,qstringofrqb,fields)
    rows = dict()
    fields = "12"
    for state in row['state']:
        rows[state] = None
    for state in rows.keys():
        qstringofrqb="{8.EX.'"+state+"'}"
        row = qb.query_table(token,tid,qstringofrqb,fields)
        dfn_list = list()
        for dfn in row['district_name']:
            dfn_list.append(str(dfn))
        rows[state] = dfn_list
    return rows

@app.route('/')
@app.route("/dailyCheck")
def dailyCheck():
    countydictdfn
    #render html
    return render_template('DailyCheck2.html', countydictdfn = countydictdfn)
    
    
@app.route('/depView/<cccounty>/', methods=['GET','POST'])
def depView(cccounty):
    #county contact info
    fields = "3"
    token ='cxeyvydbvik5y3523fepbiue8q2'
    tid = 'bk2reib52'
    qstringofrqb="{24.EX.'"+cccounty+"'}AND{13.GTE.'2017-01-01'}"
    row = qb.query_table(token,tid,qstringofrqb,fields)['record_id_']
    
    if len((request.form)) > 0:
        depid = request.form.get('d_id')
    else:
        depid = row[0]
    #render html
    return render_template('ccCreator.html', rec_id = row,county=cccounty, depid=depid)




@app.route('/pdfView/<depid>')
def pdfView(depid):
    tid = 'bk2reib52'
    url = "https://fig.quickbase.com/up/"+tid+"/a/r"+depid+"/e22/v0"
    os.system("google-chrome "+url)
    os.system('pkill chrome')
    fields = "22"
    qstringofrqb = "{3.EX."+depid+"}"
    token ='cxeyvydbvik5y3523fepbiue8q2'
    row = qb.query_table(token,tid,qstringofrqb,fields)['deposit_attachment'][0]
    pdftemp =  '/root/Downloads/'+row
    bin_pdfstage1 = open(str(pdftemp), 'rb')
    bin_pdf = bin_pdfstage1.read()
    response =make_response(bytearray(bin_pdf))
    response.mimetype = 'application/pdf'
    response.headers['Content-Disposition'] = 'inline; filename='+str(depid)
    os.remove(pdftemp)
    return response 


@app.route('/updateattach', methods=["GET","POST"])    
def updateattach():
    cccounty = request.form['county']
    depid = request.form['depid']
    usernotes = request.form['notefield']
    fields = "6"
    token ='cxeyvydbvik5y3523fepbiue8q2'
    tid = 'bk2reib52'
    qstringofrqb="{3.EX.'"+depid+"'}"
    district_id = qb.query_table(token,tid,qstringofrqb,fields)['district_id']
    url = "https://fig.quickbase.com/up/"+tid+"/a/r"+depid+"/e22/v0"
    os.system("google-chrome "+url)
    os.system('pkill chrome')
    fields = "22"
    qstringofrqb = "{3.EX."+depid+"}"
    token ='cxeyvydbvik5y3523fepbiue8q2'
    row = qb.query_table(token,tid,qstringofrqb,fields)['deposit_attachment'][0]
    pdftemp =  '/root/Downloads/'+row
    token ='cxeyvydbvik5y3523fepbiue8q2'
    tid = 'bk2q3thup'
    qb.update_table_attachment_from_file(token, tid, str(district_id), "253", cccounty, pdftemp, True)
    dict_fields_to_update = {'254': str(usernotes)}
    qb.update_record(token, tid, district_id, dict_fields_to_update)
    os.remove(pdftemp)
    return redirect(url_for('dailyCheck'))

if __name__=="__main__":
    sys_type = sys.platform
    bat_or_sh = ".bat"
    if "linux" in sys_type:
        bat_or_sh = ".sh"
    global util
    util = Utils()
    global cp
    cp = CreatePids()
    global docvc
    docvc = CreateDocv()
    args = createDictFromArgs()
    url = args.get('url')
    uid = args.get('uid')
    password = args.get('pass')
    db = args.get('db')
    countydictdfn = getCountyDict()
    sql = Sql(url,uid,password,db)
    sys.argv = ['username=bperlman@figadvisors.com','password=figtree77*']
    qb.authenticate_from_args()
#     app.run(debug=False,host="104.236.167.205",port=int("80"),ssl_context=('/root/cert.pem','/root/key.pem'))
    myport = args.get("port")
    if myport is None:
        app.run(debug=False,host="104.236.167.205")
    else:
        app.run(debug=False,host="104.236.167.205",port=myport)  