runitdir="../../pypostgres/pypg"
echo ${runitdir}
. ~/act.sh
arg="url=pg94.cxpdwhygwwwh.us-east-1.rds.amazonaws.com uid=jona_cobb password=bboc_anoj db=workhorse states=FL,CO,AZ,GA,SC,CT,NJ"
python tr.py /root/qbpython  Dailycheck.py ${arg}
