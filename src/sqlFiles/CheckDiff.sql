select b.district_full_name,d.old_fig_deposits_record_id,d.diff,d.deposit_amount 
from developer.depvspid2 d
left join billy.depvalld b 
on b.id = d.old_fig_deposits_record_id
where b.deposit_date >= '(REPLACE DATE)'
and b.state in ('(REPLACE STATE)')
/* and b.syscountyname ilike '%(REPLACE COUNTY)%' */
;