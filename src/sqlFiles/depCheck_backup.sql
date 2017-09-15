select d.deposit_amount,d.district_full_name, r.ocr_text,o.diff, d.state,r.deposit_amount,d.syscountyname
from billy.depvalld d
left join developer.rocrv r
on r.deposit_id = d.id
left join developer.depvspid2 o
on o.old_fig_deposits_record_id = r.deposit_id
where d.id = (REPLACE ID);