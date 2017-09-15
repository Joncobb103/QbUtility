'''
Created on Feb 13, 2017
quickbase_auto_redeem holds code to perform redemptions
  without any human intervention
@author: Jonathan Cobb
'''

import traceback
import qbapi.qbapi as qb
import dbqbsync.figportfolio as fap
from dbqbsync import qbflaskportfolio_saved as qbf
from qbapi.logger_init import init_root_logger
import datetime
import dbqbsync.quickbase_auto_redeem as qar

def main(args):
    logger = init_root_logger('root')
    ad = qar.create_arg_dict(args)
    parcels_in_deposits_sql_path = ad["-p"]
    # get default dates
    dt_end = datetime.datetime.now()
    dt_beg = dt_end - datetime.timedelta(days=30)
    begdate = qb.qb_date(dt_beg) # default begdate
    enddate = qb.qb_date(dt_end) # default enddate
    state_code = 'FL' # default state
    do_auto_redeem = False
    do_waterfall = False
    dep_id_list_string = None
    # see if they are on the command line
    if "-b" in ad:
        begdate = ad['-b']
    if "-e" in ad:
        enddate = ad['-e']
    if "-s" in ad:
        state_code = ad['-s']
    if "-a" in ad:
        do_auto_redeem = ad["-a"][0].lower()=='y'
    if "-w" in ad:
        do_waterfall = ad["-w"][0].lower()=='y'
    if "-l" in ad:
        dep_id_list_string = ad["-l"]

    figp = fap.FigPortfolio(app_mode_arg='live',logger_arg=logger)
    try:
        deposit_id_list=None
        if do_auto_redeem:
            ar = qar.AutoRedeem(figp=figp,begdate = begdate,enddate=enddate,
                    parcels_in_deposits_sql_path=parcels_in_deposits_sql_path,
                    state_arg=state_code,logger=logger)
            df_uploaded = ar.upload_parcels_in_deposits_between_dates()
            if df_uploaded is not None and len(df_uploaded)>0 and 'related_deposit' in df_uploaded:
                # get deposit ids
                deposit_id_list = list(set(list(df_uploaded.related_deposit)))
            else:
                logger.warn("ERROR: quickbase_auto_redeem.py: No deposit_id's returned from auto_redeem ")
        
        if do_waterfall and deposit_id_list is not None:
            if deposit_id_list is None and  dep_id_list_string is not None:
                # get list from command line
                deposit_id_list = map(lambda x: int(x),dep_id_list_string.split(","))
            qbf.qbflask_start(figp)
            u_id = 'bperlman@figadvisors.com'
            qbf.batch_waterfall(u_id, state_code, begdate, enddate,deposit_id_list=deposit_id_list)
    except figp.DfException,e:
        s = e.message
        df = e.df
        logger.warn(s)
        print df
        print traceback.format_exc()
        
