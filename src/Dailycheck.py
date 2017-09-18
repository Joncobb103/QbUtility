'''
Created on Mar 24, 2017

@author: Jonathan.Cobb
'''
import os
from flask import Flask, render_template, request, redirect,make_response
from datetime import datetime,timedelta
from Sql import Sql
import pandas as pd
from Utils import Utils
import sys
from flask.helpers import url_for,send_file
from autoRedeem import CreatePids, CreateDocv
import qbapi.qbapi as qb
import quickbase_auto_redeem as ar
from regexConverter import RegexConverter as rgc

app = Flask(__name__)
mydir = os.path.dirname(__file__)

dccontent = None
diffcontent = None
pidcontent = None
depcontent = None
todocontent = None
deppidcont = None 
depbackupcont = None
ar_fl = None
ar_all = None
ar_co = None
ar_az = None
ar_ga = None
ar_sc = None
ar_ct = None
ar_nj = None
ar_az_dub = None
ar_clerk = None
ar_idsp = None
doc_fl = None
doc_co = None
doc_az = None
doc_ga = None
qbpath = None
check = None
args = None
abbyy = None
date_str = None
statelist = None

countylogin = {'manatee' : {'url':'https://secure.taxcollector.com/ptaxweb/editWebLogin.do?action=login','username':'ar@figadvisors.com | ftcfimt@gmail.com','password':'figtree77'},\
               'putnam':{'url':'https://ptax.putnam-fl.com/ptaxweb/editWebLogin.do?action=login','username':'ar@figadvisors.com | ftcfimt@gmail.com','password':'figtree77'},\
               'charlotte':{'url':'https://or.co.charlotte.fl.us/TaxDeeds/'},\
               'osceola':{'url':'http://198.140.240.30/dt_web1/or_sch_1.asp'},\
               'pinellas':{'url':'http://www.pinellasclerk.org/tributeweb'},\
    }

def createDictFromArgs():
    argsm = sys.argv[1:]
    argMap = Utils().getArgPairs(argsm, "=")
    url = argMap.get("url")
    uid = argMap.get("uid")
    password = argMap.get("password")
    db = argMap.get("db")
    states = argMap.get("states")
    global stateslist
    if ',' in states:
        stateslist = states.split(',')
    else:
        stateslist = [states]
    state =str() 
    for astate in stateslist:
        state += "'"+str(astate)+"'"+","
    state = state[:-1]
    
    argDict = {'url':url,'uid':uid,'pass':password,'db':db,'dir':mydir,
                'state' : state, 'stateslist' : stateslist}
    return argDict

def daycheck():
    # Get args from run config
    state = args.get('state')
    weekdaytoday = datetime.today().weekday()
    
    #query check for uploads
    content = util.readFile(mydir, 'sqlFiles/Dailycheck.sql')
    if weekdaytoday == 0:
        date = datetime.date((datetime.today()- timedelta(days=3)))
    elif weekdaytoday == 6:
        date = datetime.date((datetime.today()- timedelta(days=2)))
    elif weekdaytoday == 5:
        date = datetime.date((datetime.today()- timedelta(days=1)))
    else:
        date = datetime.date((datetime.today()- timedelta(days=1)))
    query = content.replace('(REPLACE DATE)', str(date))
    query = query.replace('\'(REPLACE STATE)\'',state)
    query = query.replace(';' ,' limit 1;')
    sql = Sql(url,uid,password,db).find(query)
    if len(sql) <= 0:
        return False
    else:
        return True
    
def dateStr():
    global check
    if check:
        atab = 1
    else:
        atab = 2
        
    weekdaytoday = datetime.today().weekday()
    if weekdaytoday == 0:
        if check:
            atab = 3
        else:
            atab = 4
    elif weekdaytoday == 1:
        if check:
            atab = 1
        else:
            atab = 4
    elif weekdaytoday == 6:
        if check:
            atab = 2
        else:
            atab = 3
        
    date = datetime.date((datetime.today()- timedelta(days=atab)))
    return str(date)

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

def replaceDateAndState(content,state):
    query = content.replace('(REPLACE DATE)', date_str)
    return query.replace('\'(REPLACE STATE)\'',state)


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


def getCountyDict(mydir,state,url,uid,password,db):
    content = util.readFile(mydir,'sqlFiles/docv.sql')
    query = replaceDateAndState(content, state)
    row = sql.find(query)
    rows = dict()
    for atab in range(len(row)):
        if row[atab][2] == 'NJ':
            if rows.__contains__(row[atab][0]):
                rows[row[atab][1]].append(row[atab][3])
            else:
                rows[row[atab][1]] = [row[atab][3]]
        else:
            if rows.__contains__(row[atab][0]):
                rows[row[atab][0]].append(row[atab][3])
            else:
                rows[row[atab][0]] = [row[atab][3]]
    return rows

def setVars():
    #Read queries from file globally
    global check 
    check = daycheck()
    argsm = sys.argv[1:]
    argMap = Utils().getArgPairs(argsm, "=")
    preferred_date = argMap.get("date")
    global date_str
    if preferred_date is None:
        date_str = dateStr()
    else:
        date_str = preferred_date 
    global dccontent
    dccontent = util.readFile(mydir,'sqlFiles/Dailycheck.sql')
    global diffcontent
    diffcontent = util.readFile(mydir,'sqlFiles/CheckDiff.sql') 
    global pidcontent
    pidcontent = util.readFile(mydir,'sqlFiles/checkPid.sql')
    global depcontent
    depcontent = util.readFile(mydir,'sqlFiles/depCheck.sql')
    global depbackupcont
    depbackupcont = util.readFile(mydir,'sqlFiles/depCheck_backup.sql')
    global todocontent
    todocontent = util.readFile(mydir,'sqlFiles/todo.sql')
    global deppidcont
    deppidcont = util.readFile(mydir,'sqlFiles/searchdep.sql') 
    global ar_all
    ar_all = util.readFile(mydir,'sqlFiles/autoredeem/rocrvSqlFile_ALL_jc.sql').replace('(REPLACE DATE)',date_str)
    global ar_fl
    ar_fl = util.readFile(mydir,'sqlFiles/autoredeem/rocrvSqlFile_ALL_jc_FL.sql').replace('(REPLACE DATE)',date_str)
    global ar_co
    ar_co = util.readFile(mydir,'sqlFiles/autoredeem/rocrvSqlFile_ALL_jc_CO.sql').replace('(REPLACE DATE)',date_str) 
    global ar_az
    ar_az = util.readFile(mydir,'sqlFiles/autoredeem/rocrvSqlFile_ALL_jc_AZ.sql').replace('(REPLACE DATE)',date_str)
    global ar_ga
    ar_ga = util.readFile(mydir,'sqlFiles/autoredeem/rocrvSqlFile_ALL_jc_GA.sql').replace('(REPLACE DATE)',date_str).replace("(REPLACE STATE)", "GA")
    global ar_sc
    ar_sc = util.readFile(mydir,'sqlFiles/autoredeem/rocrvSqlFile_ALL_jc_GA.sql').replace('(REPLACE DATE)',date_str).replace("(REPLACE STATE)", "SC")
    global ar_ct
    ar_ct = util.readFile(mydir,'sqlFiles/autoredeem/rocrvSqlFile_ALL_jc_GA.sql').replace('(REPLACE DATE)',date_str).replace("(REPLACE STATE)", "CT")
    global ar_nj
    ar_nj = util.readFile(mydir,'sqlFiles/autoredeem/rocrvSqlFile_ALL_jc_NJ.sql').replace('(REPLACE DATE)',date_str).replace("(REPLACE STATE)", "NJ")
    global ar_az_dub
    ar_az_dub = util.readFile(mydir,'sqlFiles/autoredeem/rocrvSqlFile_specific_jc_AZ_dub.sql').replace('(REPLACE DATE)',date_str)
    global ar_clerk
    ar_clerk = util.readFile(mydir,'sqlFiles/autoredeem/rocrvSqlFile_specific_jc_FL_CLERK.sql').replace('(REPLACE DATE)',date_str)
    global ar_idsp
    ar_idsp = util.readFile(mydir,'sqlFiles/autoredeem/rocrvSqlFile_specific.sql')
    global doc_fl
    doc_fl = util.readFile(mydir,'sqlFiles/Docv/DocvtoPid_FL.sql').replace('(REPLACE DATE)',date_str).replace("\n", "")
    global doc_co
    doc_co = util.readFile(mydir,'sqlFiles/Docv/DocvtoPid_CO.sql').replace('(REPLACE DATE)',date_str).replace("\n", "") 
    global doc_az
    doc_az = util.readFile(mydir,'sqlFiles/Docv/DocvtoPid_AZ.sql').replace('(REPLACE DATE)',date_str).replace("\n", "")  
    global doc_ga
    doc_ga = util.readFile(mydir,'sqlFiles/Docv/DocvtoPid_AZ.sql').replace('(REPLACE DATE)',date_str).replace("\n", "")   
    global qbpath
    qbpath = util.readFile(mydir,'countytxtfolder/qbpath.txt')  
    global abbyy
    abbyy = util.readFile(mydir,'batchfiles/abbyy.txt')


@app.route('/')
@app.route("/dailyCheck/<state>")
def dailyCheck(state=None):
    qbstate = state
    if state is None:
        state = args.get('state')
    else:
        state = "'"+state+"'"
        qbstate =state
    stateslist = args.get('stateslist')
    
    #Get sql    
    query = replaceDateAndState(dccontent, state)
    query3 = replaceDateAndState(pidcontent, state)
    todo =  replaceDateAndState(todocontent, state)
    countylist = getCountyDict(mydir, state, url, uid, password, db)
    
    issues = dict()
    
    #get data returned by query
    rows = createDfFromSql1(query,url,uid,password,db)
    pid = createDfFromSql2(query3,url,uid,password,db)
    if len(pid) > 0:
        for row in range(len(pid.get('old_fig_deposits_record_id'))): 
            if pid.get('state')[row] != 'NJ':
                if pid.get('active_lien_number')[row] == None and pid.get('active_parcel')[row] == None:
                    issues[pid.get('old_fig_deposits_record_id')[row]] = "Missing active lien number or parcel"
                elif pid.get('active_lien_number')[row] == '' and pid.get('active_parcel')[row] == None:
                    issues[pid.get('old_fig_deposits_record_id')[row]] = "Missing active lien number"
                elif pid.get('active_lien_number')[row] == None and pid.get('active_parcel')[row] == '':
                    issues[pid.get('old_fig_deposits_record_id')[row]] = "Missing active parcel"
                elif pid.get('active_lien_number')[row] == '' and pid.get('active_parcel')[row] == '':
                    issues[pid.get('old_fig_deposits_record_id')[row]] = "Missing active lien number or active parcel"
                elif pid.get('active_lien_number')[row] == None and pid.get('active_parcel')[row] == None:
                    issues[pid.get('old_fig_deposits_record_id')[row]] = "Missing active lien number or active parcel"
            else:
                if pid.get('block')[row] == '' and pid.get('lot')[row] == '' and pid.get('active_lien_number')[row] == '':
                    issues[pid.get('old_fig_deposits_record_id')[row]] = "Missing block, lot, qual, & active lien number "
                elif pid.get('block')[row] == '' and pid.get('lot')[row] == '' and pid.get('active_lien_number')[row] == None:
                    issues[pid.get('old_fig_deposits_record_id')[row]] = "Missing block, lot, qual information"
                elif pid.get('block')[row] == None and pid.get('lot')[row] == None and pid.get('active_lien_number')[row] == '':
                    issues[pid.get('old_fig_deposits_record_id')[row]] = "Missing active lien number"
                elif (pid.get('block')[row] == '' or pid.get('lot')[row] == '') and pid.get('active_lien_number')[row] == '':
                    issues[pid.get('old_fig_deposits_record_id')[row]] = "Missing block or lot"
                elif (pid.get('block')[row] == '' or pid.get('lot')[row] == '') and pid.get('active_lien_number')[row] == None:
                    issues[pid.get('old_fig_deposits_record_id')[row]] = "Missing block or lot"
        if len(issues) <=0:
            issues = dict()
    fields = "26.43.8.77"
    token ='cxeyvydbvik5y3523fepbiue8q2'
    tid = 'bk2reib52'
    ids = str()
    for fid in rows.get('id'):
        ids+=str(fid)+'.'
    ids = ids[:-1]
    if qbstate is None:
        qstringofrqb="{13.GTE.'"+date_str+"'}AND{43.EX.'Unapplied'}AND({32.EX.'Florida'}OR{32.EX.'Colorado'}OR{32.EX.'Arizona'}OR{32.EX.'Georgia'}OR"+\
        "{32.EX.'South Carolina'}OR{32.EX.'Connecticut'}OR{{32.CT.'Jersey'}})"
    elif 'FL' in qbstate:
        qstringofrqb="{13.GTE.'"+date_str+"'}AND{32.EX.'Florida'}AND{43.EX.'Unapplied'}"  
    elif 'CO' in qbstate:
        qstringofrqb="{13.GTE.'"+date_str+"'}AND{32.EX.'Colorado'}AND{43.EX.'Unapplied'}"
    elif 'AZ' in qbstate:
        qstringofrqb="{13.GTE.'"+date_str+"'}AND{32.EX.'Arizona'}AND{43.EX.'Unapplied'}"
    elif 'GA' in qbstate:
        qstringofrqb="{13.GTE.'"+date_str+"'}AND{32.EX.'Georgia'}AND{43.EX.'Unapplied'}"
    elif 'SC' in qbstate:
        qstringofrqb="{13.GTE.'"+date_str+"'}AND{32.EX.'South Carolina'}AND{43.EX.'Unapplied'}"
    elif 'CT' in qbstate:
        qstringofrqb="{13.GTE.'"+date_str+"'}AND{32.EX.'Connecticut'}AND{43.EX.'Unapplied'}"
    elif 'NJ' in qbstate:
        qstringofrqb="{13.GTE.'"+date_str+"'}AND{32.CT.'Jersey'}AND{43.EX.'Unapplied'}"
    cols_i_want = ['deposit_status','old_fig_deposits_record_id','record_id','count_parcels_in_deposit']
    qbdf = pd.DataFrame(qb.query_table(token,tid,qstringofrqb,fields)).filter(items=cols_i_want)
    if len(qbdf) > 0:
        qbdf['record_id_path'] = qbdf['record_id'].apply(lambda x: qbpath+x)
        unapplied_list = str(qbdf.old_fig_deposits_record_id.tolist()).replace("'","").replace('"',"").replace("[","").replace("]","")
        todo1 = todo.replace(";", " and id in ("+unapplied_list+");")
        todolist = createDfFromSql1(todo1,url,uid,password,db)
        qbdf.old_fig_deposits_record_id = qbdf.old_fig_deposits_record_id.astype(int)
        todolist.id = todolist.id.astype(int)
        todolist = pd.merge(todolist,qbdf, how='left', left_on= 'id',right_on='old_fig_deposits_record_id')
        del todolist['id']
        todolist = todolist.rename(columns={'diff':'Deposit amount - invoiced amount'})
        todolist = todolist.to_dict()
    else:
        #return empty table
        todo1 = todo.replace(";", " and deposit_amount = 0;")
        todolist = createDfFromSql2(todo1,url,uid,password,db)
    
    global check
    global abbyy
    abbyytemp = replaceDateAndState(abbyy, state)
    #render html
    return render_template('DailyCheck2.html',results = rows, thestate = state,issues=issues
                           ,datecheck=check,todolist = todolist, contact = None,abbyy=abbyytemp,redsite=None,
                             stateslist = stateslist, countylist = countylist)



##Flask Routes##
@app.route("/dailyCheckCounty/<county>")
def dailyCheckCounty(county=None):
    state = args.get('state')
    stateslist = args.get('stateslist')
     
    #Get sql    
    query = replaceDateAndState(dccontent, state)
    query3 = replaceDateAndState(pidcontent, state)
#     clerkQuery = replaceDateAndState(clerk, state)
    todo =  replaceDateAndState(todocontent, state)
    countylist = getCountyDict(mydir, state, url, uid, password, db)
    if county is not None:
        if ',NJ' in county or ',nj' in county or ', NJ' in county or ', nj' in county:
            query = replaceDfn(query, county)
            query3 = replaceDfn(query3, county)
            todo =  replaceDfn(todo, county)
        else:
            query = replaceCounty(query, county)
            query3 = replaceCounty(query3, county)
            todo =  replaceCounty(todo, county)
    
    issues = dict()
    
    #get data returned by query
    rows = createDfFromSql1(query,url,uid,password,db)
    pid = createDfFromSql2(query3,url,uid,password,db)
    if len(pid) > 0:
        for row in range(len(pid.get('old_fig_deposits_record_id'))): 
            if pid.get('state') != 'NJ':
                if pid.get('active_lien_number')[row] == 'None' and pid.get('active_parcel')[row] == 'None':
                    issues[pid.get('old_fig_deposits_record_id')[row]] = "Missing active lien number or parcel"
                elif pid.get('active_lien_number')[row] == '' and pid.get('active_parcel')[row] == 'None':
                    issues[pid.get('old_fig_deposits_record_id')[row]] = "Missing active lien number"
                elif pid.get('active_lien_number')[row] == 'None' and pid.get('active_parcel')[row] == '':
                    issues[pid.get('old_fig_deposits_record_id')[row]] = "Missing active parcel"
                elif pid.get('active_lien_number')[row] == '' and pid.get('active_parcel')[row] == '':
                    issues[pid.get('old_fig_deposits_record_id')[row]] = "Missing active lien number or active parcel"
                elif pid.get('active_lien_number')[row] == 'None' and pid.get('active_parcel')[row] == 'None':
                    issues[pid.get('old_fig_deposits_record_id')[row]] = "Missing active lien number or active parcel"
            else:
                if pid.get('block')[row] == '' and pid.get('lot') == '' and pid.get('active_lien_number')[row] == '':
                    issues[pid.get('old_fig_deposits_record_id')[row]] = "Missing block, lot, qual, & active lien number "
                elif pid.get('block')[row] == '' and pid.get('lot') == '' and pid.get('active_lien_number')[row] == 'None':
                    issues[pid.get('old_fig_deposits_record_id')[row]] = "Missing block, lot, qual information"
                elif pid.get('block')[row] == 'None' and pid.get('lot') == 'None' and pid.get('active_lien_number')[row] == '':
                    issues[pid.get('old_fig_deposits_record_id')[row]] = "Missing active lien number"
                elif (pid.get('block')[row] == '' or pid.get('lot')[row] == '') and pid.get('active_lien_number')[row] == '':
                    issues[pid.get('old_fig_deposits_record_id')[row]] = "Missing block or lot"
                elif (pid.get('block')[row] == '' or pid.get('lot')[row] == '') and pid.get('active_lien_number')[row] == 'None':
                    issues[pid.get('old_fig_deposits_record_id')[row]] = "Missing block or lot"
        if len(issues) <=0:
            issues = dict()
    fields = "26.43.8.77"
    token ='cxeyvydbvik5y3523fepbiue8q2'
    tid = 'bk2reib52'
    ids = str()
    for fid in rows.get('id'):
        ids+=str(fid)+'.'
    ids = ids[:-1]
    qstringofrqb="{13.GTE.'"+date_str+"'}AND{24.EX.'"+county+"'}AND{43.EX.'Unapplied'}"
    cols_i_want = ['deposit_status','district_id___county','old_fig_deposits_record_id','record_id','count_parcels_in_deposit']
    qbdf = pd.DataFrame(qb.query_table(token,tid,qstringofrqb,fields)).filter(items=cols_i_want)
    if len(qbdf) > 0:
        qbdf['record_id_path'] = qbdf['record_id'].apply(lambda x: qbpath+x)
        unapplied_list = str(qbdf.old_fig_deposits_record_id.tolist()).replace("'","").replace('"',"").replace("[","").replace("]","")
        todo1 = todo.replace(";", " and id in ("+unapplied_list+");")
        todolist = createDfFromSql1(todo1,url,uid,password,db)
        qbdf.old_fig_deposits_record_id = qbdf.old_fig_deposits_record_id.astype(int)
        todolist.id = todolist.id.astype(int)
        todolist = pd.merge(todolist,qbdf, how='left', left_on= 'id',right_on='old_fig_deposits_record_id')
        del todolist['id']
        todolist = todolist.rename(columns={'diff':'Deposit amount - invoiced amount'})
        todolist = todolist.to_dict()
    else:
        #return empty table
        todo1 = todo.replace(";", " and deposit_amount = 0;")
        todolist = createDfFromSql2(todo1,url,uid,password,db)
    #county contact info
    fields = "256.258.259.260.261.264.73.250"
    tid = 'bk2q3thup'
    qstringofrqb="{9.EX.'"+county+"'}"
    contact = qb.query_table(token,tid,qstringofrqb,fields)
    if len(contact) > 0:
            del contact['update_id']
            del contact['record_id']
    try:
        if contact.empty:
            contact = None;
        else:
            contact = contact.to_html(classes='',index=False,border=0,na_rep='')
    except:
        contact = None
    global abbyy
    abbyy = replaceDateAndState(abbyy, state)
    
    
    redsite = countylogin.get(county.lower())
    #render html
    return render_template('DailyCheck2.html',datecheck=check,todolist = todolist, thestate = state, qbdf=qbdf,
                            pid = pid, stateslist = stateslist, countylist = countylist, contact = contact,abbyy=abbyy,redsite=redsite)

@app.route('/searchdep', methods=['POST'])
def searchdep():
    if request.form['depid'] is not None:
        return redirect(url_for('depView', depid = request.form['depid']))
    else:
        return redirect(url_for('dailyCheck',state = None))
    
    
@app.route('/depView/<depid>/')
def depView(depid):
    # Get args from run config
    state = args.get('state')
    stateslist = args.get('stateslist')
    
    #Get sql    
    query = deppidcont.replace('(REPLACE ID)',depid)
    
    query2 = depcontent.replace('(REPLACE ID)',depid)
    cur = sql.find(query2)
    try:
        if len(cur) == 0:
            return redirect(url_for('depBackup',depid = depid))
    except:
        return redirect(url_for('dailyCheck',state = None))
        
    
    if cur.__sizeof__() !=0:
        doc_name=cur[0][0]
        disfn = cur[0][1]
        ocr = str(cur[0][2]).decode('utf-8')
        ocr = ocr.replace(",", "").replace("$", "")
        diff = cur[0][3]
        depstate = cur[0][4]
        dep_am = cur[0][5]
        if depstate == 'NJ':
            cccounty = disfn.lower()
        else:
            cccounty = cur[0][6]
            cccounty = str(cccounty).lower()
    else:
        doc_name=None
        disfn = None
        ocr = None 
        diff = None
        depstate = None
        dep_am = None
        cccounty = None
        
    countylist = getCountyDict(mydir, state, url, uid, password, db)
    
    qb_path = None
    #get deposit id
    fields = "3"
    token ='cxeyvydbvik5y3523fepbiue8q2'
    tid = 'bk2reib52'
    qstringofrqb="{8.EX.'"+depid+"'}"
    try:
        dep_rec_id = qb.query_table(token,tid,qstringofrqb,fields).record_id[0]
        qb_path = qbpath+dep_rec_id
        
        #payment records
        fields = "3.55.23.26.29.38.57.58.70.10.11.12.17.138"
        token ='cxeyvydbvik5y3523fepbiue8q2'
        tid = 'bk2rg4v85'
        qstringofrqb="{8.EX.'"+dep_rec_id+"'}"
        payment = qb.query_table(token,tid,qstringofrqb,fields)
        if len(payment) > 0:
            del payment['update_id']
            del payment['record_id']
            payment = payment.to_html(classes='',index=False,border=0,na_rep='').replace('dataframe','report2').replace('liens_record_id__','').replace('_',' ')
        else:
            payment = None
        
    except:
        payment = None
    #get data returned by query
    pid = createDfFromSql2(query,url,uid,password,db)
    
    #county contact info
    fields = "256.258.259.260.261.264.73.250"
    tid = 'bk2q3thup'
    if depstate == 'NJ':
        qstringofrqb="{12.CT.'"+cccounty+"'}AND{15.CT.'"+depstate.upper()+"'}"
    else:
        qstringofrqb="{9.CT.'"+cccounty+"'}AND{15.CT.'"+depstate.upper()+"'}"
    contact = qb.query_table(token,tid,qstringofrqb,fields)
    if len(contact) > 0:
        del contact['update_id']
        del contact['record_id']
    try:
        if contact.empty:
            contact = None;
        else:
            contact = contact.to_html(classes='',index=False,border=0,na_rep='')
    except:
        contact = None
    
    redsite = countylogin.get(cccounty)  
    
    #get cc regex
    val = dict()
    if depstate in 'NJ':
        regexmap = util.createRegexDict(mydir, "countytxtfolder/CountyTxtFiles_Nj.xml", cccounty)
        regexmap1 = util.createRegexDict(mydir, "countytxtfolder/CountyTxtFiles_Nj2.xml", cccounty)
        regexmap2 = util.createRegexDict(mydir, "countytxtfolder/CountyTxtFiles_Nj3.xml", cccounty)
        regexmap1off = util.createRegexDict(mydir, "countytxtfolder/CountyTxtFiles_1_offs.xml", cccounty)
        if regexmap is not None:
            val['main'] = regexmap
        if regexmap1 is not None:
            val['backup'] = regexmap1
        if regexmap2 is not None:
            val['dub'] = regexmap2
        if regexmap1off is not None:
            val['one_offs'] = regexmap1off
    else:
        regexmap = util.createRegexDict(mydir, "countytxtfolder/CountyTxtFiles.xml", cccounty)
        regexmap1 = util.createRegexDict(mydir, "countytxtfolder/CountyTxtFiles2.xml", cccounty)
        regexmap2 = util.createRegexDict(mydir, "countytxtfolder/CountyTxtFiles3.xml", cccounty)
        regexmap1off = util.createRegexDict(mydir, "countytxtfolder/CountyTxtFiles_1_offs.xml", cccounty)
        if regexmap is not None:
            val['main'] = regexmap
        if regexmap1 is not None:
            val['clerk'] = regexmap1
        if regexmap2 is not None:
            val['backup'] = regexmap2
        if regexmap1off is not None:
            val['one_offs'] = regexmap1off

    #render html
    return render_template('DepCheck.html',pid = pid, stateslist = stateslist, depid=depid,ocr=ocr, qbpath=qb_path,contact=contact,dep_am=dep_am,redsite=redsite,
                           doc_name=doc_name,countylist = countylist, disfn=disfn, countyname=cccounty,diff=diff,payment=payment, depstate=depstate,dep_rec_id=dep_rec_id,val=val)

@app.route('/depBackup/<depid>/')
def depBackup(depid):
    # Get args from run config
    state = args.get('state')
    stateslist = args.get('stateslist')
    
    #Get sql    
    query = deppidcont.replace('(REPLACE ID)',depid)
    
    query2 = depbackupcont.replace('(REPLACE ID)',depid)
    cur = sql.find(query2)
    try:
        if len(cur) == 0:
            return redirect(url_for('dailyCheck',state = None))
    except:
        return redirect(url_for('dailyCheck',state = None))
        
    
    if cur.__sizeof__() !=0:
        doc_amount=cur[0][0]
        disfn = cur[0][1]
        ocr = str(cur[0][2]).decode('utf-8')
        ocr = ocr.replace(",", "").replace("$", "")
        diff = cur[0][3]
        depstate = cur[0][4]
        dep_am = cur[0][5]
        if depstate == 'NJ':
            cccounty = disfn.lower()
        else:
            cccounty = cur[0][6]
            cccounty = str(cccounty).lower()
    else:
        doc_amount=None
        disfn = None
        ocr = None 
        diff = None
        depstate = None
        dep_am = None
        cccounty = None
        
    countylist = getCountyDict(mydir, state, url, uid, password, db)
    
    #get data returned by query
    pid = createDfFromSql2(query,url,uid,password,db)
    qb_path=None
    try:
    #get deposit id
        fields = "3"
        token ='cxeyvydbvik5y3523fepbiue8q2'
        tid = 'bk2reib52'
        qstringofrqb="{8.EX.'"+depid+"'}"
        dep_rec_id = qb.query_table(token,tid,qstringofrqb,fields).record_id[0]
        qb_path = qbpath+dep_rec_id
        
            #payment records
        fields = "3.55.23.26.29.38.57.58.70.10.11.12.17.138"
        tid = 'bk2rg4v85'
        qstringofrqb="{8.EX.'"+dep_rec_id+"'}"
        payment = qb.query_table(token,tid,qstringofrqb,fields)
        if len(payment) > 0:
            del payment['update_id']
            del payment['record_id']
            payment = payment.to_html(classes='',index=False,border=0,na_rep='').replace('dataframe','report2').replace('liens_record_id__','').replace('_',' ')
        else:
            payment = None
     
    except:
        payment = None    
    
    #county contact info
    fields = "256.258.259.260.261.264.73.250"
    tid = 'bk2q3thup'
    if depstate == 'NJ':
        qstringofrqb="{12.CT.'"+cccounty+"'}AND{15.CT.'"+depstate.upper()+"'}"
    else:
        qstringofrqb="{9.CT.'"+cccounty+"'}AND{15.CT.'"+depstate.upper()+"'}"
    contact = qb.query_table(token,tid,qstringofrqb,fields)
    if len(contact) > 0:
        del contact['update_id']
        del contact['record_id']
    try:
        if contact.empty:
            contact = None;
        else:
            contact = contact.to_html(classes='',index=False,border=0,na_rep='')
    except:
        contact = None
        
    redsite = countylogin.get(cccounty)  
    
    #get cc regex
    val = dict()
    if depstate in 'NJ':
        regexmap = util.createRegexDict(mydir, "countytxtfolder/CountyTxtFiles_Nj.xml", cccounty)
        regexmap1 = util.createRegexDict(mydir, "countytxtfolder/CountyTxtFiles_Nj2.xml", cccounty)
        regexmap2 = util.createRegexDict(mydir, "countytxtfolder/CountyTxtFiles_Nj3.xml", cccounty)
        regexmap1off = util.createRegexDict(mydir, "countytxtfolder/CountyTxtFiles_1_offs.xml", cccounty)
        if regexmap is not None:
            val['main'] = regexmap
        if regexmap1 is not None:
            val['backup'] = regexmap1
        if regexmap2 is not None:
            val['dub'] = regexmap2
        if regexmap1off is not None:
            val['one_offs'] = regexmap1off
    else:
        regexmap = util.createRegexDict(mydir, "countytxtfolder/CountyTxtFiles.xml", cccounty)
        regexmap1 = util.createRegexDict(mydir, "countytxtfolder/CountyTxtFiles2.xml", cccounty)
        regexmap2 = util.createRegexDict(mydir, "countytxtfolder/CountyTxtFiles3.xml", cccounty)
        regexmap1off = util.createRegexDict(mydir, "countytxtfolder/CountyTxtFiles_1_offs.xml", cccounty)
        if regexmap is not None:
            val['main'] = regexmap
        if regexmap1 is not None:
            val['clerk'] = regexmap1
        if regexmap2 is not None:
            val['backup'] = regexmap2
        if regexmap1off is not None:
            val['one_offs'] = regexmap1off
            
    #render html
    return render_template('DepCheck_backup.html',pid = pid, stateslist = stateslist, depid=depid,ocr=ocr,qbpath=qb_path,contact=contact,dep_am=dep_am,redsite=redsite,
                           doc_amount=doc_amount,countylist = countylist, disfn=disfn, countyname=cccounty,diff=diff, payment=payment, depstate=depstate, dep_rec_id=dep_rec_id,val=val)
    
@app.route('/njCalc/<depid>')
def njCalc(depid):
    fields = "24"
    token ='cxeyvydbvik5y3523fepbiue8q2'
    tid = 'bk2reib52'
    qstringofrqb="{8.EX.'"+depid+"'}"
    dfn = qb.query_table(token,tid,qstringofrqb,fields).district_id___district_name[0]
    query = deppidcont.replace('(REPLACE ID)',depid)
    pid = createDfFromSql2(query, url, uid, password, db)
    fields = "331.460.519.592.491.183.495.492"
    tid = "bk2tb2siw"
    qbquery = "{299.EX.'"+dfn+"'}AND("
    for row in range(len(pid.get('active_lien_number'))):
        if pid.get('active_lien_number')[row] == '' or  pid.get('active_lien_number')[row] == None: 
            if pid.get('qual')[row] == '' or pid.get('qual')[row] == None:
                qbquery += '{460.CT."'+pid.get('block')[row]+' '+pid.get('lot')[row]+'"}OR'
            else:
                qbquery += '{460.CT."'+pid.get('block')[row]+' '+pid.get('lot')[row]+' '+pid.get('qual')[row]+'"}OR'
        else:
            qbquery += '{331.EX."'+pid.get('active_lien_number')[row]+'"}OR'
    qbquery = qbquery[:-2] + ')'
    calcs = qb.query_table(token, tid, qbquery, fields)
    calcs['active_lien_number'] = calcs['maximum_record_id____active_lien_number']
    if 'nj_calculation_premium_amount' not in calcs.columns:
        calcs['nj_calculation_premium_amount'] = 'no input'
    calcs = calcs[[    
    'record_id',
    'active_lien_number',   
    'block_lot_qual',     
    'nj_calculation_premium_amount',    
    'nj_calculation_non_premium_amount',    
    'nj_calculation_input_total',
    'nj_calculation_result']]
    calcs = calcs.to_html(classes='',index=False,border=0,na_rep='')
    return render_template('njCalc.html', pid=pid,calcs=calcs, depid=depid, disfn=dfn)

@app.route("/ccCreator", methods=["GET","POST"])
def ccCreator():
    depid = request.form["depid"]
    county = request.form["county"]
    state = request.form["state"]
    ocr_text = request.form["ocr"]
    quant = rgc.quantityDict
    regex = rgc.regexDict
    return render_template('ccCreator.html', quant=quant, regex=regex,ocr=ocr_text,depid=depid,county=county,state=state)

@app.route('/addParser', methods=['GET','POST'])
def addParser():
    #take all arguements
    split_key_ = "/SPLIT/"
    depid = request.form['depid']
    county = request.form['county']
    if 'validline' in request.form:
        validline = request.form['validline']
    else:
        validline = '.+'
    parcel = ""
    if 'parcel' in request.form:
        ccid = "syscountyname"
        parcellist = request.form.getlist('parcel')
        for reg in parcellist:
            parcel += str(reg)+split_key_
        parcel = parcel[:-len(split_key_)]
    cert = ""
    if 'cert' in request.form:
        certlist = request.form.getlist('cert')
        for reg in certlist:
            cert += str(reg)+split_key_
        cert = cert[:-len(split_key_)]
    block = ''
    if 'block' in request.form:
        ccid = "district_full_name"
        blocklist = request.form.getlist('block')
        for reg in blocklist:
            block += str(reg)+split_key_
        block = block[:-len(split_key_)]
    lot = ""
    if 'lot' in request.form:
        lotlist = request.form.getlist('lot')
        for reg in lotlist:
            lot += str(reg)+split_key_  
        lot = lot[:-len(split_key_)]  
    qual = ""
    if 'qual' in request.form:
        quallist = request.form.getlist('qual')
        for reg in quallist:
            qual += str(reg)+split_key_
        qual = qual[:-len(split_key_)]
    taxyear = ""
    if 'tax-year' in request.form:
        taxyearlist = request.form.getlist('tax-tear')
        for reg in taxyearlist:
            taxyear += str(reg)+split_key_
        taxyear = taxyear[:-len(split_key_)]
    lienyear = ""
    if 'lien-year' in request.form:
        lienyearlist = request.form.getlist('lien-year')
        for reg in lienyearlist:
            lienyear += str(reg)+split_key_
        lienyear = lienyear[:-len(split_key_)]
    total = ""
    if 'total' in request.form:
        totallist = request.form.getlist('total')
        for reg in totallist:
            total += str(reg)+split_key_
        total = total[:-len(split_key_)]
    multiline = request.form['multiline']
    #create countyclass xml file
    outputfolder = os.path.join(os.path.join(mydir,"CountyClassOneOff"),county+"new_XML.xml")
    util.ccCreator(outputfolder, split_key_, county, validline, cert, block,lot,qual, parcel, lienyear, taxyear, total, multiline)
    #add countyclass xml to countytxtfiles_1_offs.xml
    ctf_path = os.path.join(os.path.join(mydir,"countytxtfolder"),"CountyTxtFiles_1_offs.xml")
    util.addCcToCtf(outputfolder, ctf_path)
    #create pids if specified
    if(request.form["whattodo"] == "pids"):
        ar_idsp1 = ar_idsp.replace('(REPLACE ID)', depid)
        cp.CreatePids( url, uid, password, db, ar_idsp1, ccid,ctf_path) 
    return redirect(url_for('depView', depid = depid))
  
@app.route('/addPid', methods =['GET','POST'])    
def addPid():
    #values
    deposit_id = request.form['dpid']
    if 'parcel' in request.form.keys():
        if request.form["lien"] is not None and request.form["lien"] is not '' :
            active_lien_number = "'"+request.form["lien"]+"'" 
        else:
            active_lien_number = request.form["lien"]
        if request.form["parcel"] is not None and request.form["parcel"] is not '' :
            active_parcel = "'"+request.form["parcel"]+"'" 
        else:
            active_parcel = request.form["parcel"]
        if request.form["taxyear"] is not None and request.form["taxyear"] is not '' :
            tax_year = request.form["taxyear"]
        else:
            tax_year = None
        if request.form["taxyear"] is not None and request.form["taxyear"] is not '' :
            lien_year = request.form["lienyear"]
        else: 
            lien_year = None
    else:
        active_lien_number = None
        active_parcel = None
        tax_year = None
        lien_year = None
        
    if 'block' in request.form.keys():
        if request.form["lien"] is not None and request.form["lien"] is not '' :
            active_lien_number = "'"+request.form["lien"]+"'" 
        else:
            active_lien_number = request.form["lien"]
        if request.form["block"] is not None and request.form["block"] is not '' :
            block = "'"+request.form["block"]+"'" 
        else:
            block = request.form["block"]
        if request.form["lot"] is not None and request.form["lot"] is not '' :
            lot = "'"+request.form["lot"]+"'" 
        else:
            lot = request.form["lot"]
        if request.form["qual"] is not None and request.form["qual"] is not '' :
            qual = "'"+request.form["qual"]+"'" 
        else:
            qual = request.form["qual"]
    else:
        block = None
        lot = None
        qual = None
    
    total_per_parcel = str(request.form["total"])
    if ',' in total_per_parcel:
        total_per_parcel = total_per_parcel.replace(',','')
    #insert to db
    table = 'developer.parcels_in_deposits2'
    values = [ deposit_id, active_lien_number, active_parcel, tax_year, 
              lien_year, block, lot, qual, total_per_parcel]
    sql.insert(table, values)
    return redirect(url_for('depView',depid = deposit_id ))

@app.route('/runAbbyy', methods =['GET','POST'])
def runAbbyy():
    ablink = request.form['ablink']
    os.system('start chrome "'+ablink+'"')
    return redirect(url_for('dailyCheck' ))

@app.route('/runAbbyy_sp', methods =['GET','POST'])
def runAbbyy_sp():
    state = str(request.form['state'])
    ablink = abbyy.replace('(REPLACE DATE)', date_str)
    ablink = ablink.replace('(REPLACE STATE)',state)
    os.system('start chrome "'+ablink+'"')
    return redirect(url_for('dailyCheck' ))


@app.route('/pdfView/<d_id>')
def pdfView(d_id):
    docquery = util.readFile(mydir,'sqlFiles/docvbin.sql').replace('(REPLACE ID)',d_id)
    docvbin = sql.findOne(docquery)
    response = make_response(bytearray(docvbin[0]))
    response.mimetype = 'application/pdf'
    response.headers['Content-Disposition'] = 'inline; filename='+docvbin[1].replace(',','')
    return response 

@app.route('/sendPdf', methods=['GET','POST'])
def sendPdf():
    depid = request.form['depid']
    #get deposit id
    docquery = util.readFile(mydir,'sqlFiles/docvbin.sql').replace('(REPLACE ID)',depid)
    docvbin = sql.findOne(docquery)
    if docvbin is None:
        txtquery = util.readFile(mydir,'sqlFiles/rocrv.sql').replace('(REPLACE ID)',depid)
        ocr_text = sql.findOne(txtquery)[0]
        util.writeFile(mydir, depid+'.txt', ocr_text) 
        return send_file(os.path.join(mydir,depid+'.txt'), mimetype='application/txt', as_attachment=True)
    response = make_response(bytearray(docvbin[0]))
    if '.pdf' in docvbin[1]:
        response.mimetype = 'application/pdf'
        response.headers['Content-Disposition'] = 'attachment; filename='+depid+".pdf"
    elif '.csv' in docvbin[1]:
        response.mimetype = 'application/csv'
        response.headers['Content-Disposition'] = 'attachment; filename='+depid+".csv"
    elif '.txt' in docvbin[1]:
        if str(type(docvbin[0])) == "<type 'buffer'>" and 'PDF' in str(docvbin[0]):
            response.mimetype = 'application/pdf'
            response.headers['Content-Disposition'] = 'attachment; filename='+depid+".pdf"
        else:
            response.mimetype = 'application/txt'
            response.headers['Content-Disposition'] = 'attachment; filename='+depid+".txt"
    return response 
    
@app.route('/Updateocr', methods=['POST'])
def Updateocr():
    dep_id = request.form['depid']
    ocr_text = request.form['ocr_text']
    table = 'developer.ocr_text_local'
    checking = 'select * from '+table+' where deposit_id = '+dep_id
    try:
        ocr_text = ocr_text.replace("'","")
        ocr_text = ocr_text.replace('"',"")
        if sql.findOne(checking) is not None:
            sql.update(table, ['ocr_text'], ["'"+ocr_text+"'"], 'deposit_id', dep_id)
        else:
            values = [dep_id,"'"+ocr_text+"'"]
            sql.insert(table, values)
    except:
        print('Error updating ocr')
    return redirect(url_for('depView',depid = dep_id ))

@app.route('/CreateOcrfromfile', methods=['POST','GET'])
def CreateOcrfromfile():
    d_id = request.form['depid']
    dep_rec_id = request.form['dep_rec_id']
    #get binary from db
    depfile = request.files['newfile']
    if str(depfile.filename) is '':
        return redirect(url_for('depView',depid = d_id ))
        
    #initialize temp files
    try:
        pdftemp = os.path.join(mydir,depfile.filename)
    except:
        return redirect(url_for('depView',depid = d_id ))
    depfile.save(pdftemp)
    if ".pdf" not in pdftemp:
        ocr_text = util.readFile(mydir, depfile.filename)
        table = 'developer.ocr_text_local'
        checking = 'select * from '+table+' where deposit_id = '+d_id
        try:
            ocr_text = ocr_text.replace("'","")
            ocr_text = ocr_text.replace('"',"")
            if sql.findOne(checking) is not None:
                sql.update(table, ['ocr_text'], ["'"+ocr_text+"'"], 'deposit_id', d_id)
            else:
                values = [d_id,"'"+ocr_text+"'"]
                sql.insert(table, values)
        except:
            print('Error updating ocr')
        #update qb
        field = "22"
        token ='cxeyvydbvik5y3523fepbiue8q2'
        tid = 'bk2reib52'
        splitext = depfile.filename.split(".")
        ext = "."+splitext[1]
        qb.update_table_attachment_from_file(token, tid, dep_rec_id, field, dep_rec_id+ext, pdftemp, True)
        os.remove(pdftemp)
        return redirect(url_for('depView',depid = d_id ))
    if 'clock' in request.form:
        util.rotatePdf(pdftemp, 90, 'temptxt')
    elif 'counterclock' in request.form:
        util.rotatePdf(pdftemp, -90, 'temptxt')
    docvc.InsertOcr(url, uid, password, db, pdftemp, d_id)
    #update qb
    field = "22"
    token ='cxeyvydbvik5y3523fepbiue8q2'
    tid = 'bk2reib52'
    qb.update_table_attachment_from_file(token, tid, dep_rec_id, field, depfile.filename, pdftemp, True)
    os.remove(pdftemp)
    return redirect(url_for('depView',depid = d_id ))


@app.route('/DeletePid', methods=['POST'])
def DeletePid():
    dep_id = request.form['depid']
    table = 'developer.parcels_in_deposits2'
    sql.delete(table, 'old_fig_deposits_record_id', dep_id)
    return redirect(url_for('depView',depid = dep_id ))

@app.route('/CreateOcr', methods=['POST','GET'])
def CreateOcr():
    d_id = request.form['depid']
    #get binary from db
    try:
        table = 'developer.ocr_text_local'
        sql.delete(table, 'deposit_id', d_id)
    except:
        pass
    #get binary from db
    docquery = util.readFile(mydir,'sqlFiles/docvbin.sql').replace('(REPLACE ID)',d_id)
    docvbin = sql.findOne(docquery)
    #create a pdf
    pdffile = open(os.path.join(mydir,'temptxt/temp.pdf'),'wb')
    pdffile.write(bytearray(docvbin[0]))
    pdffile.close()
    #initialize temp files
    pdftemp = os.path.join(mydir,'temptxt/temp.pdf')
    if 'clock' in request.form:
        util.rotatePdf(pdftemp, 90, 'temptxt')
    elif 'counterclock' in request.form:
        util.rotatePdf(pdftemp, -90, 'temptxt')
    docvc.InsertOcr(url, uid, password, db, pdftemp, d_id)
    os.remove(pdftemp)
    return redirect(url_for('depView',depid = d_id ))


@app.route('/createPid', methods=['POST'])
def createPid():
    countytxtpath = os.path.join(mydir,'countytxtfolder\CountyTxtFiles.xml')
    countytxtpath2 = os.path.join(mydir,'countytxtfolder\CountyTxtFiles2.xml')
    countytxtpath3 = os.path.join(mydir,'countytxtfolder\CountyTxtFiles3.xml')
    countytxtpath_nj = os.path.join(mydir,'countytxtfolder\CountyTxtFiles_NJ.xml')
    countytxtpath_nj2 = os.path.join(mydir,'countytxtfolder\CountyTxtFiles_NJ2.xml')
    countytxtpath_nj3 = os.path.join(mydir,'countytxtfolder\CountyTxtFiles_NJ3.xml')
    countytxtpath1offs = os.path.join(mydir,'countytxtfolder\CountyTxtFiles_1_offs.xml')
    njccid = "district_full_name"
    ccid = "syscountyname"
    state = str(request.form['state'])
    if 'AZ' in state:
        cp.CreatePids( url, uid, password, db, ar_az, ccid, countytxtpath)
        cp.CreatePids( url, uid, password, db, ar_az, ccid, countytxtpath3)
        cp.CreatePidsOverride( url, uid, password, db, ar_az_dub, ccid, countytxtpath3)
        cp.CreatePids( url, uid, password, db, ar_az, ccid, countytxtpath1offs)
    elif 'FL' in state:
        cp.CreatePids( url, uid, password, db, ar_fl, ccid, countytxtpath)
        cp.CreatePids( url, uid, password, db, ar_clerk, ccid, countytxtpath2)
        cp.CreatePids( url, uid, password, db, ar_fl, ccid, countytxtpath3)
        cp.CreatePids( url, uid, password, db, ar_fl, ccid, countytxtpath1offs)
    elif 'CO' in state:
        cp.CreatePids( url, uid, password, db, ar_co, ccid, countytxtpath)
        cp.CreatePids( url, uid, password, db, ar_co, ccid, countytxtpath3)
        cp.CreatePids( url, uid, password, db, ar_co, ccid, countytxtpath1offs)
    elif 'GA' in state:
        cp.CreatePids( url, uid, password, db, ar_ga, ccid, countytxtpath)
        cp.CreatePids( url, uid, password, db, ar_ga, ccid, countytxtpath3)
        cp.CreatePids( url, uid, password, db, ar_ga, ccid, countytxtpath1offs)
    elif 'SC' in state:
        cp.CreatePids( url, uid, password, db, ar_sc, ccid, countytxtpath)
        cp.CreatePids( url, uid, password, db, ar_sc, ccid, countytxtpath3)
        cp.CreatePids( url, uid, password, db, ar_sc, ccid, countytxtpath1offs)
    elif 'CT' in state:
        cp.CreatePids( url, uid, password, db, ar_ct, ccid, countytxtpath)
        cp.CreatePids( url, uid, password, db, ar_ct, ccid, countytxtpath3)
        cp.CreatePids( url, uid, password, db, ar_ct, ccid, countytxtpath1offs)
    elif 'NJ' in state:
        cp.CreatePids( url, uid, password, db, ar_nj, njccid,  countytxtpath_nj)
        cp.CreatePids( url, uid, password, db, ar_nj, njccid, countytxtpath_nj2)
        cp.CreatePidsOverride( url, uid, password, db, ar_nj, njccid, countytxtpath_nj3)
    else:
        cp.CreatePids( url, uid, password, db, ar_all, ccid, countytxtpath)
        cp.CreatePids( url, uid, password, db, ar_all, ccid, countytxtpath3)
        cp.CreatePidsOverride( url, uid, password, db, ar_az_dub, ccid, countytxtpath3)
        cp.CreatePids( url, uid, password, db, ar_all, ccid, countytxtpath1offs)
        cp.CreatePids( url, uid, password, db, ar_clerk, ccid, countytxtpath2)
        cp.CreatePids( url, uid, password, db, ar_nj, njccid,  countytxtpath_nj)
        cp.CreatePids( url, uid, password, db, ar_nj, njccid, countytxtpath_nj2)
        cp.CreatePidsOverride( url, uid, password, db, ar_nj, njccid, countytxtpath_nj3)
    return redirect(url_for('dailyCheck',state = None))

@app.route('/CreatePidSp', methods=['POST'])
def CreatePidSp():
    dep_id = request.form['depid']
    state = request.form['state']
    ccid = ""
    if state == 'NJ':
        ccid = "district_full_name"
    else:
        ccid = "syscountyname"
    countytxtpath = os.path.join(mydir,'countytxtfolder\CountyTxtFiles.xml')
    countytxtpath2 = os.path.join(mydir,'countytxtfolder\CountyTxtFiles2.xml')
    countytxtpath3 = os.path.join(mydir,'countytxtfolder\CountyTxtFiles3.xml')
    countytxtpath_nj = os.path.join(mydir,'countytxtfolder\CountyTxtFiles_NJ.xml')
    countytxtpath_nj2 = os.path.join(mydir,'countytxtfolder\CountyTxtFiles_NJ2.xml')
    countytxtpath_nj3 = os.path.join(mydir,'countytxtfolder\CountyTxtFiles_NJ3.xml')
    countytxtpath1offs = os.path.join(mydir,'countytxtfolder\CountyTxtFiles_1_offs.xml')
    ar_idsp1 = ar_idsp.replace('(REPLACE ID)', dep_id)
    if state == 'NJ':
        if 'backup' in request.form:
            cp.CreatePids( url, uid, password, db, ar_idsp1, ccid, countytxtpath_nj2)
        elif 'dub' in request.form:
            cp.CreatePids( url, uid, password, db, ar_idsp1, ccid, countytxtpath_nj)
            cp.CreatePidsOverride( url, uid, password, db, ar_idsp1, ccid, countytxtpath_nj3)
        else:
            cp.CreatePids( url, uid, password, db, ar_idsp1, ccid, countytxtpath_nj)
        return redirect(url_for('depView',depid = dep_id ))
    if 'clerk' in request.form:
        cp.CreatePids( url, uid, password, db, ar_idsp1, ccid,countytxtpath2)
    elif 'azdub' in request.form:
        cp.CreatePids( url, uid, password, db, ar_idsp1, ccid,countytxtpath)    
        cp.CreatePidsOverride( url, uid, password, db, ar_idsp1, ccid,countytxtpath3)
    elif 'dub' in request.form:
        cp.CreatePids( url, uid, password, db, ar_idsp1, ccid,countytxtpath3)
    elif 'oneoffs' in request.form:
        cp.CreatePids( url, uid, password, db, ar_idsp1, ccid,countytxtpath1offs)
    else:
        cp.CreatePids( url, uid, password, db, ar_idsp1, ccid,countytxtpath)
        
    return redirect(url_for('depView',depid = dep_id ))


@app.route('/createDocv', methods=['POST'])
def createDocv():
    state = request.form['state']
    if 'AZ' in state:
        docvc.Docv( url, uid, password, db, doc_az)
    elif 'FL' in state:
        docvc.Docv( url, uid, password, db, doc_fl)
    elif 'CO' in state:
        docvc.DocvCo( url, uid, password, db, doc_co)
    elif 'GA' in state:
        docvc.DocvCo( url, uid, password, db, doc_ga)
    return redirect(url_for('dailyCheck',state = None))

@app.route('/other')
def other():
    return render_template('other.html')

@app.route('/gacsv', methods=['POST'])
def gacsv():
    batchf = os.path.join(mydir,'batchfiles/parsefromfolder'+bat_or_sh)
    os.system(batchf)
    return render_template('other.html')


@app.route('/DeleteAPid/<depid>', methods=['POST'])
def DeleteAPid(depid):
    table = 'developer.parcels_in_deposits2'
    query = deppidcont.replace('where d.id = (REPLACE ID)', 'where p.id = (REPLACE ID)')
    for pidid in request.form:
        query = query.replace('(REPLACE ID)', pidid)
        sql.delete(table, 'id', pidid)
    return redirect(url_for('depView',depid = depid ))

@app.route('/editPid/<pidid>/<state>')
def editPid(pidid,state):
    query = deppidcont.replace("where d.id = (REPLACE ID)","where p.id = (REPLACE ID)")
    query = query.replace('(REPLACE ID)',pidid)
    pidrecfromid = createDfFromSql2(query, url, uid, password, db)
    return render_template('editpids.html', pid = pidrecfromid, state=state)

@app.route('/updatePid', methods =['GET','POST'])    
def updatePid():
    #values
    pid_id = request.form['pidid']
    col =[]
    values=[] 
    if 'parcel' in request.form.keys():
        if request.form["lien"] is not None and request.form["lien"] is not '' and request.form["lien"] != 'None':
            values.append("'"+request.form["lien"]+"'") 
            col.append('active_lien_number')
        if request.form["parcel"] is not None and request.form["parcel"] is not '' and request.form["parcel"] != 'None':
            values.append("'"+request.form["parcel"]+"'") 
            col.append('active_parcel')
        if request.form["taxyear"] is not None and request.form["taxyear"] is not '' and request.form["taxyear"] != 'None':
            values.append(request.form["taxyear"])
            col.append('tax_year')
        if request.form["lienyear"] is not None and request.form["lienyear"] is not '' and request.form["lienyear"] != 'None':
            values.append(request.form["lienyear"])
            col.append('lien_year') 
    if 'qual' in request.form.keys():
        if request.form["qual"] is not None and request.form["qual"] is not '' and request.form["qual"] != 'None':
            values.append("'"+request.form["qual"]+"'") 
            col.append('qual')
        if request.form["lot"] is not None and request.form["lot"] is not '' and request.form["lot"] != 'None':
            values.append("'"+request.form["lot"]+"'") 
            col.append('lot')
        if request.form["block"] is not None and request.form["block"] is not '' and request.form["block"] != 'None':
            values.append(request.form["block"])
            col.append('block')
    total_per_parcel = str(request.form["total"])
    if ',' in total_per_parcel:
        total_per_parcel = total_per_parcel.replace(',','')
    values.append(total_per_parcel)
    col.append('total_per_parcel')
    
    #insert to db
    table = 'developer.parcels_in_deposits2'
    sql.update(table, col,values,'id', pid_id)
    return render_template('editpids.html', pid = None)

@app.route('/autoRedeem_sp',  methods=['POST','GET'])
def autoRedeem_sp():
    dep_id = request.form['depid']
    state = request.form['depstate']
    ar_sp_query = util.readFile(mydir,'batchfiles/autoRedeem/autoRedeem.sql').replace('OLDFIGLIST',dep_id)
    util.writeFile(mydir, 'batchfiles/autoRedeem/temp.sql', ar_sp_query)
    argm = util.readFile(mydir,'batchfiles/autoRedeem/autoRedeem.txt').replace('%1',state)
    argm = argm.replace('autoRedeem.sql','temp.sql')
    argl = str(argm).split(' ')
    try:
        ar.main(argl)
    except Exception,e:
        print e
    return redirect(url_for('depView',depid = dep_id ))

@app.route('/autoRedeem', methods=['POST'])
def autoRedeem():
    state = request.form['state']
    if state == None or state == '':
        for states in stateslist:
            argm = util.readFile(mydir,'batchfiles/autoRedeem/autoRedeem.txt').replace('%1',states)
            argl = str(argm).split(' ')
            try:
                ar.main(argl)
            except Exception,e:
                print e
        return redirect(url_for('dailyCheck',state = None))
        
    argm = util.readFile(mydir,'batchfiles/autoRedeem/autoRedeem.txt').replace('%1',state)
    argl = str(argm).split(' ')
    try:
        ar.main(argl)
    except Exception,e:
        print e
    return redirect(url_for('dailyCheck',state = None))
 
    

@app.route('/reports')  
def reports(state=None):
    f_o_m = date_str
#     f_o_m = '2017-07-14'
    payment_high_int_message = ""
    #Payments table
    fields = "34.3.8.55.23.26.29.38.57.58.70.10.11.12.17.138.174.135"
    token ='cxeyvydbvik5y3523fepbiue8q2'
    tid = 'bk2rg4v85'
    qstringofrqb="{174.GTE.'.45'}AND{19.GTE.'"+f_o_m+"'}AND{140.XCT.'Yes'}"
    if state is not None:
        qstringofrqb+="AND{35.EX.'"+state+"'}"
    payment_high_int = qb.query_table(token,tid,qstringofrqb,fields)
    if len(payment_high_int) > 0:
        payment_high_int['invoice_interest'] = payment_high_int['invoice_interest'].astype(float)
        payment_high_int['invoice_purchase_amount'] = payment_high_int['invoice_purchase_amount'].astype(float)
        del payment_high_int['update_id']
        payment_high_int['record_id'] = payment_high_int['deposits_record_id'].apply(lambda x: qbpath+x)
        for col in payment_high_int.columns:
            if str(col) == 'record_id':
                continue
            col_new = col.replace('liens_record_id__','').replace('_',' ')
            payment_high_int.rename(columns={col : col_new}, inplace=True)
            
             
    qstringofrqb="{17.LT.'_FID_29'}AND{17.GT.'0'}AND{70.GT.'0'}AND{19.GTE.'"+f_o_m+"'}AND{136.XCT.'Partial payment correctly applied'}"
    if state is not None:
        qstringofrqb+="AND{35.EX.'"+state+"'}"
    fields = "34.3.8.55.23.26.29.38.57.58.70.10.11.12.17.138.135"
    payment_partial = qb.query_table(token,tid,qstringofrqb,fields)
    if len(payment_partial) > 0:
        payment_partial['record_id'] = payment_partial['deposits_record_id'].apply(lambda x: qbpath+x)
        for col in payment_partial.columns:
            if str(col) == 'record_id':
                continue
            col_new = col.replace('liens_record_id__','').replace('_',' ')
            payment_partial.rename(columns={col : col_new}, inplace=True) 
        
        
        
    qstringofrqb="{70.XEX.'0'}AND{19.GTE.'"+f_o_m+"'}"
    if state is not None:
        qstringofrqb+="AND{35.EX.'"+state+"'}"
    payment_error_upf = qb.query_table(token,tid,qstringofrqb,fields)
    if len(payment_error_upf) > 0:
        payment_error_upf['record_id'] = payment_error_upf['deposits_record_id'].apply(lambda x: qbpath+x)
        for col in payment_error_upf.columns:
            if str(col) == 'record_id':
                continue
            col_new = col.replace('liens_record_id__','').replace('_',' ')
            payment_error_upf.rename(columns={col : col_new}, inplace=True) 
    
    #payment_redemption_review    
    qstringofrqb="{140.EX.''}AND{19.GTE.'"+f_o_m+"'}AND({70.GT.'0'}OR{138.GT.'0'}OR{70.LT.'0'}OR{138.LT.'0'})"
    if state is not None:
        qstringofrqb+="AND{35.EX.'"+state+"'}"
    payment_redemption_review = qb.query_table(token,tid,qstringofrqb,fields)
    if len(payment_redemption_review) > 0:
        payment_redemption_review['record_id'] = payment_redemption_review['deposits_record_id'].apply(lambda x: qbpath+x)
        for col in payment_redemption_review.columns:
            if str(col) == 'record_id':
                continue
            col_new = col.replace('liens_record_id__','').replace('_',' ')
            payment_redemption_review.rename(columns={col : col_new}, inplace=True)     
        
        #payment_negative invoiced    
    qstringofrqb="({11.LT.0}OR{10.LT.0})AND{19.GTE.'"+f_o_m+"'}"
    if state is not None:
        qstringofrqb+="AND{35.EX.'"+state+"'}"
    payment_neg_inv = qb.query_table(token,tid,qstringofrqb,fields)
    if len(payment_neg_inv) > 0:
        payment_neg_inv['record_id'] = payment_neg_inv['deposits_record_id'].apply(lambda x: qbpath+x)
        for col in payment_neg_inv.columns:
            if str(col) == 'record_id':
                continue
            col_new = col.replace('liens_record_id__','').replace('_',' ')
            payment_neg_inv.rename(columns={col : col_new}, inplace=True)     
        
    payment_high_int = payment_high_int.to_dict()
    payment_partial = payment_partial.to_dict()
    payment_error_upf = payment_error_upf.to_dict()
    payment_redemption_review = payment_redemption_review.to_dict()
    payment_neg_inv = payment_neg_inv.to_dict()
     
    fields = "34.12.32.35"
    token ='cxeyvydbvik5y3523fepbiue8q2'
    tid = 'bk2reib52'
    qstringofrqb="{13.EX.'"+f_o_m+"'}"
    if state is not None:
        qstringofrqb+="AND{32.EX.'"+state+"'}"
    deposit_vs_payments = pd.DataFrame(qb.query_table(token,tid,qstringofrqb,fields))
    deposit_vs_payments['deposit_amount'] = deposit_vs_payments['deposit_amount'].astype(float)
    if 'total_invoice' in deposit_vs_payments.columns:
        deposit_vs_payments['total_invoice'] = deposit_vs_payments['total_invoice'].astype(float)
    else:
        deposit_vs_payments['total_invoice'] = 0.0
    if 'deposit_check_to_total_invoice' in deposit_vs_payments.columns:
        deposit_vs_payments['deposit_check_to_total_invoice'] = deposit_vs_payments['deposit_check_to_total_invoice'].astype(float)
    else:
        deposit_vs_payments['deposit_check_to_total_invoice'] = 0.0
    deposit_vs_payments['diff'] = deposit_vs_payments['deposit_check_to_total_invoice']
    del deposit_vs_payments['deposit_check_to_total_invoice']
    states_for_today = deposit_vs_payments['district_id___state'].unique().tolist()
    deposit_vs_payments=deposit_vs_payments.groupby(by=['district_id___state']).sum().to_html(classes='',index=True,border=0,na_rep='').replace('_',' ').replace('dataframe','dvp')
 
     
    fields = "24.3.12.34.8"
    token ='cxeyvydbvik5y3523fepbiue8q2'
    tid = 'bk2reib52'
    qstringofrqb="{13.EX.'"+date_str+"'}AND{34.GT.'0'}AND{12.XEX._FID_34}"
    if state is not None:
        qstringofrqb+="AND{32.EX.'"+state+"'}"
    dep_over_under = pd.DataFrame(qb.query_table(token,tid,qstringofrqb,fields))
    if len(dep_over_under) > 0:
        dep_over_under['record_id'] = dep_over_under['record_id'].apply(lambda x: qbpath+x)
        for col in dep_over_under.columns:
            if str(col) == 'record_id':
                continue
            col_new = col.replace('liens_record_id__','').replace('_',' ')
            dep_over_under.rename(columns={col : col_new}, inplace=True)     
    dep_over_under = dep_over_under.to_dict()
 
    return render_template('reports.html', payment_high_int = payment_high_int,payment_partial = payment_partial,dep_over_under=dep_over_under,
                           payment_high_int_message=payment_high_int_message, payment_error_upf = payment_error_upf, payment_neg_inv=payment_neg_inv,
                           payment_redemption_review=payment_redemption_review,deposit_vs_payments=deposit_vs_payments,states_for_today=states_for_today)



@app.route('/reports_for_state/<state>')  
def reports_for_state(state=None):
    f_o_m = date_str
    payment_high_int_message = ""
    #Payments table
    fields = "34.3.8.55.23.26.29.38.57.58.70.10.11.12.17.138.174.135"
    token ='cxeyvydbvik5y3523fepbiue8q2'
    tid = 'bk2rg4v85'
    qstringofrqb="{174.GTE.'.30'}AND{19.GTE.'"+f_o_m+"'}AND{140.XCT.'Yes'}"
    if state is not None:
        qstringofrqb+="AND{35.EX.'"+state+"'}"
    payment_high_int = qb.query_table(token,tid,qstringofrqb,fields)
    if len(payment_high_int) > 0:
        payment_high_int['invoice_interest'] = payment_high_int['invoice_interest'].astype(float)
        payment_high_int['invoice_purchase_amount'] = payment_high_int['invoice_purchase_amount'].astype(float)
        del payment_high_int['update_id']
        payment_high_int['record_id'] = payment_high_int['deposits_record_id'].apply(lambda x: qbpath+x)
        for col in payment_high_int.columns:
            if str(col) == 'record_id':
                continue
            col_new = col.replace('liens_record_id__','').replace('_',' ')
            payment_high_int.rename(columns={col : col_new}, inplace=True)
            
             
    qstringofrqb="{17.LT.'_FID_29'}AND{17.GT.'0'}AND{70.GT.'0'}AND{19.GTE.'"+f_o_m+"'}AND{136.XCT.'Partial payment correctly applied'}"
    if state is not None:
        qstringofrqb+="AND{35.EX.'"+state+"'}"
    fields = "34.3.8.55.23.26.29.38.57.58.70.10.11.12.17.138.135"
    payment_partial = qb.query_table(token,tid,qstringofrqb,fields)
    if len(payment_partial) > 0:
        payment_partial['record_id'] = payment_partial['deposits_record_id'].apply(lambda x: qbpath+x)
        for col in payment_partial.columns:
            if str(col) == 'record_id':
                continue
            col_new = col.replace('liens_record_id__','').replace('_',' ')
            payment_partial.rename(columns={col : col_new}, inplace=True) 
        
        
        
    qstringofrqb="{70.XEX.'0'}AND{19.GTE.'"+f_o_m+"'}"
    if state is not None:
        qstringofrqb+="AND{35.EX.'"+state+"'}"
    payment_error_upf = qb.query_table(token,tid,qstringofrqb,fields)
    if len(payment_error_upf) > 0:
        payment_error_upf['record_id'] = payment_error_upf['deposits_record_id'].apply(lambda x: qbpath+x)
        for col in payment_error_upf.columns:
            if str(col) == 'record_id':
                continue
            col_new = col.replace('liens_record_id__','').replace('_',' ')
            payment_error_upf.rename(columns={col : col_new}, inplace=True) 
    
    #payment_redemption_review    
    qstringofrqb="{140.EX.''}AND{19.GTE.'"+f_o_m+"'}AND({70.GT.'0'}OR{138.GT.'0'}OR{70.LT.'0'}OR{138.LT.'0'})"
    if state is not None:
        qstringofrqb+="AND{35.EX.'"+state+"'}"
    payment_redemption_review = qb.query_table(token,tid,qstringofrqb,fields)
    if len(payment_redemption_review) > 0:
        payment_redemption_review['record_id'] = payment_redemption_review['deposits_record_id'].apply(lambda x: qbpath+x)
        for col in payment_redemption_review.columns:
            if str(col) == 'record_id':
                continue
            col_new = col.replace('liens_record_id__','').replace('_',' ')
            payment_redemption_review.rename(columns={col : col_new}, inplace=True)    
    
        #payment_negative invoiced    
    qstringofrqb="({11.LT.0}OR{10.LT.0})AND{19.GTE.'"+f_o_m+"'}"
    if state is not None:
        qstringofrqb+="AND{35.EX.'"+state+"'}"
    payment_neg_inv = qb.query_table(token,tid,qstringofrqb,fields)
    if len(payment_neg_inv) > 0:
        payment_neg_inv['record_id'] = payment_neg_inv['deposits_record_id'].apply(lambda x: qbpath+x)
        for col in payment_neg_inv.columns:
            if str(col) == 'record_id':
                continue
            col_new = col.replace('liens_record_id__','').replace('_',' ')
            payment_neg_inv.rename(columns={col : col_new}, inplace=True)     
        
    payment_high_int = payment_high_int.to_dict()
    payment_partial = payment_partial.to_dict()
    payment_error_upf = payment_error_upf.to_dict()
    payment_redemption_review = payment_redemption_review.to_dict()
    payment_neg_inv = payment_neg_inv.to_dict()
     
    fields = "34.12.32.35"
    token ='cxeyvydbvik5y3523fepbiue8q2'
    tid = 'bk2reib52'
    qstringofrqb="{13.EX.'"+date_str+"'}"
    if state is not None:
        qstringofrqb+="AND{32.EX.'"+state+"'}"
    deposit_vs_payments = pd.DataFrame(qb.query_table(token,tid,qstringofrqb,fields))
    deposit_vs_payments['deposit_amount'] = deposit_vs_payments['deposit_amount'].astype(float)
    deposit_vs_payments['total_invoice'] = deposit_vs_payments['total_invoice'].astype(float)
    if 'deposit_check_to_total_invoice' in deposit_vs_payments.columns:
        deposit_vs_payments['deposit_check_to_total_invoice'] = deposit_vs_payments['deposit_check_to_total_invoice'].astype(float)
    else:
        deposit_vs_payments['deposit_check_to_total_invoice'] = 0.0
    deposit_vs_payments['diff'] = deposit_vs_payments['deposit_check_to_total_invoice']
    del deposit_vs_payments['deposit_check_to_total_invoice']
    deposit_vs_payments=deposit_vs_payments.groupby(by=['district_id___state']).sum().to_html(classes='',index=True,border=0,na_rep='').replace('_',' ').replace('dataframe','dvp')
    
    fields = "24.3.12.34.8"
    token ='cxeyvydbvik5y3523fepbiue8q2'
    tid = 'bk2reib52'
    qstringofrqb="{13.EX.'"+date_str+"'}AND{34.GT.'0'}AND{12.XEX._FID_34}"
    if state is not None:
        qstringofrqb+="AND{32.EX.'"+state+"'}"
    dep_over_under = pd.DataFrame(qb.query_table(token,tid,qstringofrqb,fields))
    if len(dep_over_under) > 0:
        dep_over_under['record_id'] = dep_over_under['deposits_record_id'].apply(lambda x: qbpath+x)
        for col in dep_over_under.columns:
            if str(col) == 'record_id':
                continue
            col_new = col.replace('liens_record_id__','').replace('_',' ')
            dep_over_under.rename(columns={col : col_new}, inplace=True)     
    dep_over_under = dep_over_under.to_dict()
    
    qstringofrqb="{13.EX.'"+date_str+"'}"
    try:
        states_for_today = pd.DataFrame(qb.query_table(token,tid,qstringofrqb,fields))['district_id___state'].unique().tolist()
    except:
        states_for_today = []
    return render_template('reports.html', payment_high_int = payment_high_int,payment_partial = payment_partial,dep_over_under=dep_over_under,
                           payment_high_int_message=payment_high_int_message, payment_error_upf = payment_error_upf, payment_neg_inv=payment_neg_inv,
                           payment_redemption_review=payment_redemption_review,deposit_vs_payments=deposit_vs_payments,states_for_today=states_for_today)



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
    sql = Sql(url,uid,password,db)
    setVars()
    sys.argv = ['username=bperlman@figadvisors.com','password=figtree77*']
    qb.authenticate_from_args()
    app.run(debug=False)